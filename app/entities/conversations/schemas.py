from dataclasses import dataclass


@dataclass(slots=True)
class ConversationCreate:
    title: str


@dataclass(slots=True)
class ConversationUpdate:
    title: str
