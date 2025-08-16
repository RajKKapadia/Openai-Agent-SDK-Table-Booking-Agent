from agents import Agent, OpenAIResponsesModel
from openai import AsyncOpenAI

from src import config
from src.tools.current_date_tool import fetch_current_date_time
from src.tools.join_waitlist_tool import JoinWaitlistTool
from src.tools.save_booking_tool import SaveBookingTool
from src.tools.table_availability_tool import FetchTableAvailabilityTool
from src.utils.prompts import TABLE_BOOKING_AGENT_PROMPT
from src.models.schemas import UserInfo


table_booking_agent = Agent[UserInfo](
    name="Table Booking Agent",
    tools=[
        fetch_current_date_time,
        FetchTableAvailabilityTool,
        SaveBookingTool,
        JoinWaitlistTool,
    ],
    model=OpenAIResponsesModel(
        model=config.OPENAI_AGENT_MODEL,
        openai_client=AsyncOpenAI(api_key=config.OPENAI_API_KEY),
    ),
    instructions=TABLE_BOOKING_AGENT_PROMPT,
)
