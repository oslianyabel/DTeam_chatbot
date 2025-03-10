from pydantic import BaseModel


class Message(BaseModel):
    thread_id: str | None
    message: str


class AssistantMessage(Message):
    assistant_id: str


class UserMessage(Message):
    user_id: str


class UserAssistantMessage(AssistantMessage):
    user_id: str
