from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from src.config import Config

BASE_DIR = Path(__file__).resolve().parent


mail_config = ConnectionConfig(
    MAIL_USERNAME=Config.MAIL_USERNAME,
    MAIL_PASSWORD=Config.MAIL_PASSWORD,
    MAIL_FROM=Config.MAIL_FROM,
    MAIL_PORT=587,
    MAIL_SERVER=Config.MAIL_SERVER,
    MAIL_FROM_NAME=Config.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    # TEMPLATE_FOLDER=Path(BASE_DIR, 'templates'),
)

mail = FastMail(config=mail_config)

def create_message(recipients: list[str], subject: str, body: str) -> MessageSchema:
    message = MessageSchema(
        subject=subject,
        body=body,
        recipients=recipients,
        subtype=MessageType.html,
    )
    return message
