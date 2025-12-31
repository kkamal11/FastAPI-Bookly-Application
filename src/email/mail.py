from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from config import env_config
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent

mail_config = ConnectionConfig(
    MAIL_USERNAME = env_config.MAIL_USERNAME,
    MAIL_PASSWORD = env_config.MAIL_PASSWORD, 
    MAIL_FROM = env_config.MAIL_FROM,
    MAIL_PORT = env_config.MAIL_PORT,
    MAIL_SERVER = env_config.MAIL_SERVER,
    MAIL_FROM_NAME = env_config.MAIL_FROM_NAME,
    MAIL_STARTTLS = env_config.MAIL_STARTTLS,
    MAIL_SSL_TLS = env_config.MAIL_SSL_TLS,
    USE_CREDENTIALS = env_config.USE_CREDENTIALS,
    VALIDATE_CERTS = env_config.VALIDATE_CERTS,
    TEMPLATE_FOLDER = Path(BASE_DIR, "templates")
)

mail = FastMail(
    config = mail_config
)

def create_message(recipients: List[str], subject: str, body: str) -> MessageSchema:
    message = MessageSchema(
        recipients=recipients,
        subject=subject,
        body=body,
        subtype=MessageType.html
    )
    return message


