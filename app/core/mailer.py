import smtplib
from email.message import EmailMessage

from fastapi import HTTPException, status

from app.core.config import settings


def _ensure_smtp_configured() -> None:
	if not settings.smtp_host or not settings.smtp_username or not settings.smtp_password or not settings.smtp_from_email:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="SMTP is not configured. Set SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD, and SMTP_FROM_EMAIL.",
		)


def send_password_reset_email(to_email: str, username: str, reset_link: str) -> None:
	_ensure_smtp_configured()

	message = EmailMessage()
	message["Subject"] = "Reset your ReWordify password"
	message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
	message["To"] = to_email
	message.set_content(
		(
			f"Hi {username},\n\n"
			"We received a request to reset your password for ReWordify.\n"
			f"Reset link: {reset_link}\n\n"
			"This link expires in 30 minutes. If you did not request this, you can ignore this email.\n"
		)
	)

	with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as server:
		if settings.smtp_use_tls:
			server.starttls()
		server.login(settings.smtp_username, settings.smtp_password)
		server.send_message(message)


def send_signup_otp_email(to_email: str, username: str, otp: str) -> None:
	_ensure_smtp_configured()

	message = EmailMessage()
	message["Subject"] = "Verify your ReWordify account"
	message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
	message["To"] = to_email
	message.set_content(
		(
			f"Hi {username},\n\n"
			"Your ReWordify verification OTP is:\n\n"
			f"{otp}\n\n"
			"This OTP expires in 10 minutes.\n"
		)
	)

	with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as server:
		if settings.smtp_use_tls:
			server.starttls()
		server.login(settings.smtp_username, settings.smtp_password)
		server.send_message(message)