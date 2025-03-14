import logging
import smtplib
from email.message import EmailMessage

from chatbot.core.config import config

logger = logging.getLogger(__name__)


def send_email(EMAIL_TO, subject, message):
    if config.ENVIRONMENT != "prod":
        return True

    logger.debug(f"Enviando correo a {EMAIL_TO}")
    EMAIL = config.EMAIL
    PASSWORD = config.EMAIL_PASSWORD
    HOST = config.EMAIL_HOST

    email = EmailMessage()
    email["from"] = EMAIL
    email["to"] = EMAIL_TO
    email["subject"] = "Dteam_chatbot: " + subject
    email.set_content(message)

    try:
        with smtplib.SMTP(HOST, port=587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL, PASSWORD)
            smtp.sendmail(EMAIL, EMAIL_TO, email.as_string())

        logger.info(f"Correo enviado a {EMAIL_TO}")
        return True

    except Exception as exc:
        logger.error(f"Error enviando correo a {EMAIL_TO}: {exc}")
        return False
