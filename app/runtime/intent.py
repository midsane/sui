from app.entities.messages.models import Message
from app.llms.service import LLMService

from .schemas import Intent

SYSTEM_PROMPT = """
You are an intent classifier for an AI coding agent.

Determine whether the user's latest message should be handled as normal
conversation or whether the assistant should execute actions using tools.

Return EXACTLY one word.

chat

or

execute

Choose "chat" if the user is:
- asking questions
- requesting explanations
- requesting code examples
- asking for debugging advice
- asking for comparisons
- discussing concepts

Examples:

User: What is Docker?
chat

User: Explain async await.
chat

User: Write a Python binary search.
chat

Choose "execute" if the assistant needs to perform work.

Examples:

User: Create a FastAPI project.
execute

User: Create main.py and requirements.txt.
execute

User: Clone this repository.
execute

User: Run the tests.
execute

User: Search today's AI news.
execute

User: Fix the failing unit tests.
execute

Rules:
- Return exactly one word.
- No punctuation.
- No markdown.
- No explanation.
""".strip()


class IntentRouter:
    def __init__(
        self,
        llm_service: LLMService,
    ) -> None:
        self.llm_service = llm_service

    async def classify(
        self,
        history: list[Message],
    ) -> Intent:
        result = await self.llm_service.llm_call(
            messages=history,
            system_prompt=SYSTEM_PROMPT,
        )

        match result.text.strip().lower():
            case "execute":
                return Intent.EXECUTE

            case "chat":
                return Intent.CHAT

            case _:
                return Intent.CHAT
