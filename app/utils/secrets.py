"""AWS Secrets Manager utilities."""

import json
import logging
from typing import Optional

import boto3
from botocore.exceptions import ClientError

from app.config import get_settings

logger = logging.getLogger(__name__)


def get_secret(secret_name: Optional[str] = None) -> Optional[dict]:
    """
    Fetch secret from AWS Secrets Manager.

    Args:
        secret_name: Name of the secret to fetch. Uses settings if not provided.

    Returns:
        Dictionary containing secret values, or None if not found.
    """
    settings = get_settings()
    secret_name = secret_name or settings.aws_secret_name

    if not secret_name:
        logger.debug("No secret name configured, skipping Secrets Manager")
        return None

    try:
        client = boto3.client(
            service_name="secretsmanager",
            region_name=settings.aws_region,
        )

        response = client.get_secret_value(SecretId=secret_name)

        if "SecretString" in response:
            return json.loads(response["SecretString"])

        logger.warning("Secret found but contains binary data, not JSON")
        return None

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code == "ResourceNotFoundException":
            logger.warning(f"Secret '{secret_name}' not found")
        elif error_code == "AccessDeniedException":
            logger.error(f"Access denied to secret '{secret_name}'")
        else:
            logger.error(f"Error fetching secret: {e}")
        return None
    except json.JSONDecodeError:
        logger.error("Secret value is not valid JSON")
        return None


def get_db_credentials() -> dict:
    """
    Get database credentials from Secrets Manager or environment.

    Returns:
        Dictionary with keys: host, port, dbname, username, password
    """
    settings = get_settings()

    # Try to get from Secrets Manager first
    secret = get_secret()

    if secret:
        password = secret.get("password")

        # If password_secret_arn is set, fetch password from the managed secret
        if not password and secret.get("password_secret_arn"):
            try:
                client = boto3.client(
                    service_name="secretsmanager",
                    region_name=settings.aws_region,
                )
                pwd_response = client.get_secret_value(
                    SecretId=secret["password_secret_arn"]
                )
                if "SecretString" in pwd_response:
                    pwd_secret = json.loads(pwd_response["SecretString"])
                    password = pwd_secret.get("password")
                    logger.info("Retrieved password from managed secret")
            except Exception as e:
                logger.error(f"Error fetching password from managed secret: {e}")

        return {
            "host": secret.get("host", settings.db_host),
            "port": int(secret.get("port", settings.db_port)),
            "dbname": secret.get("dbname", settings.db_name),
            "username": secret.get("username", settings.db_user),
            "password": password or settings.db_password,
        }

    # Fall back to environment variables
    return {
        "host": settings.db_host,
        "port": settings.db_port,
        "dbname": settings.db_name,
        "username": settings.db_user,
        "password": settings.db_password,
    }
