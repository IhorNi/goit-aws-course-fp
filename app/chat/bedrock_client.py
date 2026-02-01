"""AWS Bedrock chat client using LangChain."""

import logging
from typing import Any, Dict, Generator, List, Optional

from langchain_aws import ChatBedrock
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from app.config import get_settings

logger = logging.getLogger(__name__)

# Type alias for chat history (Gradio 5+ format: list of {role, content} dicts)
ChatHistory = List[Dict[str, Any]]


class BedrockChatClient:
    """Chat client for AWS Bedrock using LangChain."""

    def __init__(
        self,
        model_id: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        region: Optional[str] = None,
    ):
        """
        Initialize Bedrock chat client.

        Args:
            model_id: Bedrock model ID.
            max_tokens: Maximum tokens in response.
            temperature: Model temperature for randomness.
            region: AWS region.
        """
        settings = get_settings()

        self.model_id = model_id or settings.bedrock_model_id
        self.max_tokens = max_tokens or settings.bedrock_max_tokens
        self.temperature = temperature or settings.bedrock_temperature
        self.region = region or settings.aws_region

        self._client: Optional[ChatBedrock] = None
        self._system_message = (
            "You are a helpful AI assistant. Provide clear, accurate, "
            "and concise responses to user questions."
        )

    @property
    def client(self) -> ChatBedrock:
        """Get or create LangChain ChatBedrock client."""
        if self._client is None:
            self._client = ChatBedrock(
                model_id=self.model_id,
                region_name=self.region,
                model_kwargs={
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature,
                },
            )
            logger.info(f"Bedrock client initialized with model: {self.model_id}")

        return self._client

    def set_system_message(self, message: str) -> None:
        """Set the system message for the conversation."""
        self._system_message = message

    def _build_messages(
        self, user_message: str, history: Optional[ChatHistory] = None
    ) -> List[BaseMessage]:
        """
        Build message list from history and new user message.

        Args:
            user_message: Current user message.
            history: Chat history as list of {role, content} dicts (Gradio 5+ format).

        Returns:
            List of LangChain message objects.
        """
        messages: List[BaseMessage] = []

        # Add system message
        if self._system_message:
            messages.append(SystemMessage(content=self._system_message))

        # Add history (Gradio 5+ format: list of {role, content} dicts)
        if history:
            for msg in history:
                role = msg.get("role", "")
                content = msg.get("content", "")
                if isinstance(content, str) and content:
                    if role == "user":
                        messages.append(HumanMessage(content=content))
                    elif role == "assistant":
                        messages.append(AIMessage(content=content))

        # Add current user message
        messages.append(HumanMessage(content=user_message))

        return messages

    def chat(
        self, user_message: str, history: Optional[ChatHistory] = None
    ) -> str:
        """
        Send a message and get a response.

        Args:
            user_message: User's message.
            history: Chat history as list of {role, content} dicts.

        Returns:
            Assistant's response.
        """
        if not user_message.strip():
            return "Please enter a message."

        try:
            messages = self._build_messages(user_message, history)
            response = self.client.invoke(messages)
            return response.content

        except Exception as e:
            logger.error(f"Chat error: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

    def chat_stream(
        self, user_message: str, history: Optional[ChatHistory] = None
    ) -> Generator[str, None, None]:
        """
        Send a message and stream the response.

        Args:
            user_message: User's message.
            history: Chat history as list of {role, content} dicts.

        Yields:
            Chunks of the assistant's response.
        """
        if not user_message.strip():
            yield "Please enter a message."
            return

        try:
            messages = self._build_messages(user_message, history)

            full_response = ""
            for chunk in self.client.stream(messages):
                if chunk.content:
                    full_response += chunk.content
                    yield full_response

        except Exception as e:
            logger.error(f"Chat stream error: {e}")
            yield f"Sorry, I encountered an error: {str(e)}"


# Global client instance
_chat_client: Optional[BedrockChatClient] = None


def get_chat_client() -> BedrockChatClient:
    """Get or create global chat client instance."""
    global _chat_client

    if _chat_client is None:
        _chat_client = BedrockChatClient()

    return _chat_client
