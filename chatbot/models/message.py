from pydantic import BaseModel


class Message(BaseModel):
    chat_id: str | None
    message: str


class MessageIn(Message):
    secret: str


class MessageOut(Message):
    interactions: int


class AssistantMessage(Message):
    assistant_id: str


class UserMessage(Message):
    user_id: str


class UserAssistantMessage(AssistantMessage):
    user_id: str
