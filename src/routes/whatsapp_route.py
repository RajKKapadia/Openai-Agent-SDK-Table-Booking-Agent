import hmac
import hashlib
import json
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Request, Query
import httpx

from src import config
from src import logging
from src.queue import whatsapp_queue

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


def send_whatsapp_message_sync(phone_number: str, message: str) -> Dict[str, Any]:
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
    logger.info("Sending message:")
    logger.info(f"Receiver: {phone_number}, Message: {message}")
    with httpx.Client() as client:
        try:
            response = client.post(url, json=payload, headers=headers)
            logger.info(response)
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


def process_whatsapp_message(message_data: Dict[str, Any]) -> Optional[Dict[str, str]]:
    try:
        if "messages" in message_data:
            message = message_data["messages"][0]
            from_number = message.get("from")
            message_type = message.get("type")
            content = ""
            if message_type == "text":
                content = message.get("text", {}).get("body", "")
                return {
                    "from": from_number,
                    "type": message_type,
                    "content": content,
                    "timestamp": message.get("timestamp"),
                }
            else:
                return None
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
    return None


@router.post("/webhook", status_code=200)
async def handle_post_webhook(request: Request):
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
                                message_info = process_whatsapp_message(value)
                                if message_info:
                                    logger.info(
                                        f"Received message from {message_info['from']}: {message_info['content']}"
                                    )
                                    response_text = f"Echo: {message_info['content']}"
                                    job = whatsapp_queue.enqueue(
                                        send_whatsapp_message_sync,
                                        message_info["from"],
                                        response_text,
                                    )
                                    logger.info(job.id)
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
