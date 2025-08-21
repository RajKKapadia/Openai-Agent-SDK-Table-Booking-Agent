from agents import Agent, OpenAIResponsesModel
from openai import AsyncOpenAI

from src import config
from src.schemas.schemas import TableBookingOutput
from src.utils.prompts import GAURDRAIL_PROMPT


guardrail_agent = Agent(
    name="Gaurdrail Check",
    instructions=GAURDRAIL_PROMPT,
    output_type=TableBookingOutput,
    model=OpenAIResponsesModel(
        model=config.OPENAI_GUARDRAIL_MODEL,
        openai_client=AsyncOpenAI(api_key=config.OPENAI_API_KEY),
    ),
)
