from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Final

logger = logging.getLogger(__name__)

# Provider presets: name → (smtp_host, smtp_port, password_hint)
# Used by the CLI setup wizard only.
SMTP_PROVIDERS: Final[dict[str, tuple[str | None, int | None, str]]] = {
    "Gmail": ("smtp.gmail.com", 587, "App password (get one at https://myaccount.google.com/apppasswords)"),
    "Outlook / Hotmail": ("smtp.office365.com", 587, "Password or app password"),
    "Yahoo Mail": ("smtp.mail.yahoo.com", 587, "App password (required)"),
    "iCloud Mail": ("smtp.mail.me.com", 587, "App-specific password"),
    "Zoho Mail": ("smtp.zoho.com", 587, "Password"),
    "Other": (None, None, "SMTP password"),
}


class EmailNotifier:
    def __init__(
        self,
        from_email: str,
        to_email: str,
        password: str,
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587,
    ) -> None:
        self._from_email = from_email
        self._to_email = to_email
        self._password = password
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port

    def validate(self) -> None:
        if not self._from_email:
            raise ValueError("from_email is required for EmailNotifier")
        if not self._to_email:
            raise ValueError("to_email is required for EmailNotifier")
        if not self._password:
            raise ValueError("password is required for EmailNotifier")
        if not self._smtp_host:
            raise ValueError("smtp_host is required for EmailNotifier")
        if not self._smtp_port:
            raise ValueError("smtp_port is required for EmailNotifier")

    def send(self, subject: str, message: str) -> None:
        msg = MIMEMultipart()
        msg["From"] = self._from_email
        msg["To"] = self._to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))
        try:
            server = smtplib.SMTP(self._smtp_host, self._smtp_port)
            server.starttls()
            server.login(self._from_email, self._password)
            server.send_message(msg)
            server.quit()
            logger.info("Email sent to %s", self._to_email)
        except smtplib.SMTPException as e:
            logger.error("SMTP error: %s", e)
            raise
