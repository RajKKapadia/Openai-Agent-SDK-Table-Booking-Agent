from typing import List

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    message: str
    status: int


class ChatHistory(BaseModel):
    query: str
    response: str


class AgentChatRequest(BaseModel):
    query: str
    chat_history: List[ChatHistory] = Field(default_factory=list, alias=["chatHistory"])
    user_id: str = Field(alias=["userId"])


class AgentChatResponse(BaseModel):
    type: str
    content: str


class TableBookingOutput(BaseModel):
    is_table_booking: bool
    reasoning: str


class UserInfo(BaseModel):
    uid: str
