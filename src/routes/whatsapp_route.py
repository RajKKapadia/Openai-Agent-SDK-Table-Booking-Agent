import hmac
import hashlib
import json
from typing import Dict, Any

from agents import Runner
from arq import ArqRedis
from fastapi import APIRouter, HTTPException, Request, Query, Depends
import httpx
from sqlalchemy import select
from openai import AsyncOpenAI

from src import config
from src import logging
from src.custom_agents.table_booking_agent import table_booking_agent
from src.database import get_database_session
from src.models.chat_model import Message, User
from src.custom_agents.guard_rail_agent import guardrail_agent
from src.schemas.schemas import TableBookingOutput, UserInfo
from src.utils.prompts import GAURDRAIL_FAIL_PROMPT

router = APIRouter(prefix=f"/api/{config.API_VERSION}/whatsapp", tags=["WhatsApp"])

logger = logging.getLogger(__name__)


@router.get("/webhook")
async def handle_get_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    logger.info(hub_challenge)
    logger.info(hub_mode)
    logger.info(hub_verify_token)
    if hub_mode == "subscribe" and hub_verify_token == config.VERIFY_TOKEN:
        logger.info("Webhook verified successfully")
        return int(hub_challenge)
    else:
        logger.warning("Webhook verification failed")
        raise HTTPException(status_code=403, detail="Verification failed")


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    if not config.APP_SECRET:
        logger.warning("APP_SECRET not configured")
        return False

    expected_signature = hmac.new(
        config.APP_SECRET.encode("utf-8"), payload, hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(f"sha256={expected_signature}", signature)


GRAPH_API_VERSION = "v22.0"
GRAPH_API_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


async_client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)


async def send_whatsapp_message(phone_number: str, message: str) -> Dict[str, Any]:
    url = f"{GRAPH_API_URL}/{config.PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {config.ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": message},
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error sending message: {e.response.status_code} - {e.response.text}"
            )
            raise HTTPException(
                status_code=e.response.status_code, detail=e.response.text
            )
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))


async def process_whatsapp_message(ctx: Any, from_number: str, query: str) -> None:
    try:
        db = await get_database_session()
        logger.info("Creating a new database session...")

        logger.info("Getting DB User...")
        result = await db.execute(select(User).filter(User.whatsapp_id == from_number))
        db_user = result.scalars().first()
        if not db_user:
            db_user = User(whatsapp_id=from_number)
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
        logger.info(db_user)

        logger.info("Getting previous messages...")
        result = await db.execute(
            select(Message)
            .filter(Message.user_id == db_user.id)
            .order_by(Message.created_at.desc())
            .limit(config.CHAT_HISTORY_LIMIT)
        )
        chat_history = result.scalars().all()
        formatted_chat_history = [
            {"role": msg.role.value, "content": msg.content} for msg in chat_history
        ]
        formatted_chat_history.append({"role": "user", "content": query})
        logger.info(formatted_chat_history)

        logger.info("Asking assistant...")
        input_checks = await Runner.run(
            starting_agent=guardrail_agent, input=formatted_chat_history
        )
        final_output = input_checks.final_output_as(TableBookingOutput)
        logger.info("Gaurdrail response:")
        logger.info(final_output)
        if final_output.is_table_booking:
            result = await Runner.run(
                starting_agent=table_booking_agent,
                input=formatted_chat_history,
                context=UserInfo(uid=from_number),
            )
            response = result.final_output
        else:
            completion = await async_client.chat.completions.create(
                model=config.OPENAI_AGENT_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": GAURDRAIL_FAIL_PROMPT.format(query=query),
                    },
                ],
            )
            response = completion.choices[0].message.content
        logger.info(response)

        logger.info("Saving message...")
        db.add(Message(user_id=db_user.id, role="user", content=query))
        await db.commit()
        db.add(Message(user_id=db_user.id, role="assistant", content=response))
        await db.commit()

        await send_whatsapp_message(phone_number=from_number, message=response)
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
    finally:
        await db.close()
        logger.info("Database session closed...")
        return None


@router.post("/webhook", status_code=200)
async def handle_post_webhook(
    request: Request, redis_pool: ArqRedis = Depends(config.get_redis_pool)
):
    try:
        body = await request.body()
        signature = request.headers.get("X-Hub-Signature-256", "")
        if config.APP_SECRET and not verify_webhook_signature(body, signature):
            logger.warning("Invalid webhook signature")
            raise HTTPException(status_code=403, detail="Invalid signature")
        data = json.loads(body.decode("utf-8"))
        if "entry" in data:
            for entry in data["entry"]:
                if "changes" in entry:
                    for change in entry["changes"]:
                        if change.get("field") == "messages":
                            value = change.get("value", {})
                            if "messages" in value:
                                message = value["messages"][0]
                                from_number = message.get("from")
                                message_type = message.get("type")
                                content = None
                                if message_type == "text":
                                    content = message.get("text", {}).get("body", "")
                                if content:
                                    logger.info(
                                        f"Received message from {from_number}: {content}"
                                    )
                                    job = await redis_pool.enqueue_job(
                                        "process_whatsapp_message", from_number, content
                                    )
                                    logger.info(f"Job Id: {job.job_id}")
                            elif "statuses" in value:
                                for status in value["statuses"]:
                                    logger.info(
                                        f"Message status update: {status.get('status')} for message {status.get('id')}"
                                    )
        return "OK"
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
