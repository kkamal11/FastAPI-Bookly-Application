from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from config import env_config
from pathlib import Path
from typing import List
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"

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
    TEMPLATE_FOLDER = TEMPLATE_DIR
)


class EmailService:
    """Service for sending emails using FastAPI-Mail."""
    def __init__(self):
        self.mail = FastMail(mail_config)
    
    def create_message(self, recipients: List[str], subject: str, body: str) -> MessageSchema:
        message = MessageSchema(
            recipients=recipients,
            subject=subject,
            body=body,
            subtype=MessageType.html
        )
        return message

    async def send_html_mail_to_user_email(
        self,
        email: str,
        subject: str,
        html_template_data: str,
        html_template_name
    ):
        template_body = {}
        template_body["expiry_time"] = "10 minutes"
        for k, v in html_template_data.items():
            template_body[k] = v
        message = MessageSchema(
            subject=subject,
            recipients=[email],
            template_body=template_body,
            subtype=MessageType.html,
        )

        await self.mail.send_message(
            message,
            template_name=html_template_name
        )