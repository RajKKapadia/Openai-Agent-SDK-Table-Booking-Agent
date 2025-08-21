from typing import List

from agents import FunctionTool, RunContextWrapper
from pydantic import BaseModel, Field

from src.schemas.schemas import UserInfo
from src import logging

logger = logging.getLogger(__name__)


class FetchTableAvailabilityToolInput(BaseModel):
    restaurant_name: str = Field(
        description="Name of the restaurant to get table information"
    )
    date: str = Field(description="Reservation date, format dd/mm/yyyy")
    time_window: List[str] = Field(
        description="Reservation time window, start time, end time, end time can be 00:00, format hh:mm"
    )
    number_of_person: int = Field(
        description="Number of people to book reservation for"
    )


async def fetch_table_availability(
    ctx: RunContextWrapper[UserInfo], args: FetchTableAvailabilityToolInput
) -> str:
    """Call the actual API here"""
    logger.info("Inside the Fetch Table Availability.")
    logger.info(args)
    logger.info(ctx)
    return f"We have seats available at {args.restaurant_name} for {args.date}."


async def run_fetch_table_availability(
    ctx: RunContextWrapper[UserInfo], args: str
) -> str:
    """The arguments are passed here as a string, we need to validate it using the Pydantic Model."""
    parsed_args = FetchTableAvailabilityToolInput.model_validate_json(args)
    return await fetch_table_availability(ctx=ctx, args=parsed_args)


FetchTableAvailabilityTool = FunctionTool(
    name="fetch_table_availability",
    description="Fetch the table availability at the restaurant via API call.",
    params_json_schema=FetchTableAvailabilityToolInput.model_json_schema(),
    on_invoke_tool=run_fetch_table_availability,
    strict_json_schema=False,
)
