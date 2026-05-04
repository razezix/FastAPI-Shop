import logging
from decimal import Decimal
from uuid import UUID

from src.core.config import get_settings
from src.domain.services.email_service import AbstractEmailService

logger = logging.getLogger(__name__)


class SMTPEmailService(AbstractEmailService):
    def __init__(self) -> None:
        self._settings = get_settings()

    async def send_order_confirmation(self, to: str, order_id: UUID, total: Decimal) -> None:
        await self._send(
            to=to,
            subject="Order Confirmation",
            body=f"Your order #{order_id} has been placed. Total: ${total}",
        )

    async def send_order_status_update(self, to: str, order_id: UUID, new_status: str) -> None:
        await self._send(
            to=to,
            subject=f"Order #{order_id} status updated",
            body=f"Your order #{order_id} status changed to: {new_status}",
        )

    async def send_welcome_email(self, to: str, first_name: str) -> None:
        await self._send(
            to=to,
            subject="Welcome to Online Shop!",
            body=f"Hi {first_name}, welcome to Online Shop! Start browsing our products.",
        )

    async def _send(self, to: str, subject: str, body: str) -> None:
        if not self._settings.SMTP_HOST or not self._settings.SMTP_USER:
            logger.info("Email (SMTP not configured): to=%s subject=%s", to, subject)
            return
        try:
            import aiosmtplib
            from email.mime.text import MIMEText

            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = self._settings.SMTP_FROM_EMAIL
            msg["To"] = to

            await aiosmtplib.send(
                msg,
                hostname=self._settings.SMTP_HOST,
                port=self._settings.SMTP_PORT,
                username=self._settings.SMTP_USER or None,
                password=self._settings.SMTP_PASSWORD or None,
                start_tls=True,
            )
        except Exception as e:
            logger.error("Failed to send email to %s: %s", to, e)
