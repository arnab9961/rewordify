from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def hash_password(password: str) -> str:
	return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
	return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
	expires_delta = timedelta(minutes=expires_minutes or settings.access_token_expire_minutes)
	expire_at = datetime.now(timezone.utc) + expires_delta
	payload = {"sub": subject, "exp": expire_at}
	return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
	return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])


def is_valid_token(token: str) -> bool:
	try:
		decode_access_token(token)
		return True
	except JWTError:
		return False