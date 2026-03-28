from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


class EmailNotifier:
    def __init__(self, from_email: str, to_email: str, password: str) -> None:
        self._from_email = from_email
        self._to_email = to_email
        self._password = password

    def validate(self) -> None:
        if not self._from_email:
            raise ValueError("from_email is required for EmailNotifier")
        if not self._to_email:
            raise ValueError("to_email is required for EmailNotifier")
        if not self._password:
            raise ValueError("password is required for EmailNotifier")

    def send(self, subject: str, message: str) -> None:
        msg = MIMEMultipart()
        msg["From"] = self._from_email
        msg["To"] = self._to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(self._from_email, self._password)
            server.send_message(msg)
            server.quit()
            logger.info("Email sent to %s", self._to_email)
        except smtplib.SMTPException as e:
            logger.error("SMTP error: %s", e)
            raise
