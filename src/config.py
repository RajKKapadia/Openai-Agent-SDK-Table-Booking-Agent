import os

from dotenv import load_dotenv, find_dotenv
from agents import set_tracing_disabled
from redis import Redis
from arq.connections import create_pool

set_tracing_disabled(disabled=True)

load_dotenv(find_dotenv())

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERVER_API_KEY = os.getenv("SERVER_API_KEY")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
APP_SECRET = os.getenv("APP_SECRET")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

API_VERSION = "v0"

OPENAI_AGENT_MODEL = "gpt-4.1-mini"
OPENAI_GUARDRAIL_MODEL = "gpt-4.1-mini"

ERROR_MESSAGE = "We are facing an issue, please try after sometimes."

CHAT_HISTORY_LIMIT = 15

redis_conn = Redis(host="localhost", port=6379, db=0)


async def get_redis_pool():
    return await create_pool()
