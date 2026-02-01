"""Chat module with AWS Bedrock integration."""

from app.chat.bedrock_client import BedrockChatClient, get_chat_client

__all__ = ["BedrockChatClient", "get_chat_client"]
