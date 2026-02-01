"""Main Gradio application entry point."""

import logging
import sys
from typing import Any, Dict, Generator, List

import gradio as gr

from app.auth.auth_handler import gradio_auth
from app.auth.database import check_database_connection, init_database
from app.chat.bedrock_client import get_chat_client
from app.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Type alias for chat history (Gradio 5+ format)
ChatHistory = List[Dict[str, Any]]


def chat_response(
    message: str, history: ChatHistory
) -> Generator[str, None, None]:
    """
    Generate chat response with streaming.

    Args:
        message: User's message.
        history: Chat history.

    Yields:
        Streamed response chunks.
    """
    client = get_chat_client()
    yield from client.chat_stream(message, history)


def create_app() -> gr.Blocks:
    """Create and configure the Gradio application."""
    settings = get_settings()

    with gr.Blocks(title=settings.app_name) as app:
        gr.Markdown(
            f"""
            # {settings.app_name}
            Welcome! Ask me anything and I'll do my best to help.
            """
        )

        gr.ChatInterface(fn=chat_response)

        gr.Markdown(
            """
            ---
            *Powered by AWS Bedrock with Mistral*
            """
        )

    return app


def main() -> None:
    """Run the Gradio application."""
    settings = get_settings()

    logger.info(f"Starting {settings.app_name}")
    logger.info(f"Auth enabled: {settings.auth_enabled}")
    logger.info(f"Debug mode: {settings.debug}")

    # Initialize database if auth is enabled
    if settings.auth_enabled:
        logger.info("Checking database connection...")
        if check_database_connection():
            logger.info("Database connection successful")
            init_database()
        else:
            logger.error("Database connection failed!")
            if not settings.debug:
                sys.exit(1)

    # Create application
    app = create_app()

    # Configure authentication
    auth = None
    if settings.auth_enabled:
        auth = gradio_auth
        logger.info("Authentication enabled")

    # Launch application
    app.launch(
        server_name=settings.app_host,
        server_port=settings.app_port,
        auth=auth,
        auth_message="Please login to access the chatbot",
        show_error=settings.debug,
    )


if __name__ == "__main__":
    main()