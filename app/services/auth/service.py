import hashlib
import secrets
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

from app.core.config import settings
from app.core.db import get_database
from app.core.mailer import send_password_reset_email, send_signup_otp_email
from app.core.security import hash_password, verify_password
from app.services.auth.schema import (
	AuthUser,
	ForgotPasswordRequest,
	HistoryItem,
	LoginRequest,
	ProfileResponse,
	ResetPasswordRequest,
	SignupRequest,
	VerifySignupOtpRequest,
)
from app.services.history.service import history_service


def _serialize_user(document: dict[str, Any]) -> AuthUser:
	return AuthUser(
		id=str(document["_id"]),
		username=document["username"],
		email=document["email"],
		created_at=document.get("created_at"),
	)


class AuthService:
	async def create_signup_otp(self, payload: SignupRequest) -> None:
		db = get_database()
		username = payload.username.strip().lower()
		email = payload.email.lower().strip()

		existing_user = await db.users.find_one({"$or": [{"username": username}, {"email": email}]})
		if existing_user:
			raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email already exists.")

		username_conflict = await db.signup_otps.find_one({"username": username, "email": {"$ne": email}})
		if username_conflict:
			raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username is already pending verification.")

		otp = f"{secrets.randbelow(900000) + 100000}"
		otp_hash = hashlib.sha256(otp.encode("utf-8")).hexdigest()
		expires_at = datetime.now(timezone.utc).timestamp() + (10 * 60)

		await db.signup_otps.update_one(
			{"email": email},
			{
				"$set": {
					"username": username,
					"email": email,
					"password_hash": hash_password(payload.password),
					"otp_hash": otp_hash,
					"expires_at": expires_at,
					"attempts": 0,
					"updated_at": datetime.now(timezone.utc),
				},
				"$setOnInsert": {"created_at": datetime.now(timezone.utc)},
			},
			upsert=True,
		)

		send_signup_otp_email(to_email=email, username=username, otp=otp)

	async def verify_signup_otp(self, payload: VerifySignupOtpRequest) -> AuthUser:
		db = get_database()
		email = payload.email.lower().strip()
		record = await db.signup_otps.find_one({"email": email})
		if not record:
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP.")

		now_ts = datetime.now(timezone.utc).timestamp()
		if record.get("expires_at", 0) < now_ts:
			await db.signup_otps.delete_one({"_id": record["_id"]})
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP expired. Please register again.")

		otp_hash = hashlib.sha256(payload.otp.strip().encode("utf-8")).hexdigest()
		if otp_hash != record.get("otp_hash"):
			await db.signup_otps.update_one({"_id": record["_id"]}, {"$inc": {"attempts": 1}})
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP.")

		user_document = {
			"username": record["username"],
			"email": record["email"],
			"password_hash": record["password_hash"],
			"created_at": datetime.now(timezone.utc),
		}
		try:
			result = await db.users.insert_one(user_document)
		except DuplicateKeyError as exc:
			raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email already exists.") from exc

		await db.signup_otps.delete_one({"_id": record["_id"]})
		created = await db.users.find_one({"_id": result.inserted_id})
		return _serialize_user(created)

	async def authenticate(self, payload: LoginRequest) -> AuthUser:
		db = get_database()
		identifier = payload.identifier.strip().lower()
		user = await db.users.find_one({"$or": [{"username": identifier}, {"email": identifier}]})
		if not user or not verify_password(payload.password, user["password_hash"]):
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username/email or password.")
		return _serialize_user(user)

	async def get_user_by_id(self, user_id: str) -> AuthUser | None:
		db = get_database()
		try:
			object_id = ObjectId(user_id)
		except (InvalidId, TypeError):
			return None
		user = await db.users.find_one({"_id": object_id})
		if not user:
			return None
		return _serialize_user(user)

	async def build_profile(self, user_id: str) -> ProfileResponse:
		user = await self.get_user_by_id(user_id)
		if user is None:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

		recent_history = await history_service.get_recent_history(user_id, limit=10)
		total_history = await history_service.get_history_count(user_id)
		return ProfileResponse(user=user, recent_history=[HistoryItem(**item) for item in recent_history], total_history=total_history)

	async def request_password_reset(self, payload: ForgotPasswordRequest) -> None:
		db = get_database()
		email = payload.email.lower().strip()
		user = await db.users.find_one({"email": email})

		# Keep response generic so account existence is not disclosed.
		if not user:
			return

		token = secrets.token_urlsafe(32)
		token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
		expires_at = datetime.now(timezone.utc).timestamp() + (30 * 60)

		await db.password_reset_tokens.insert_one(
			{
				"user_id": user["_id"],
				"token_hash": token_hash,
				"expires_at": expires_at,
				"used": False,
				"created_at": datetime.now(timezone.utc),
			}
		)

		reset_link = f"{settings.app_base_url}/reset-password?token={token}"
		send_password_reset_email(
			to_email=user["email"],
			username=user["username"],
			reset_link=reset_link,
		)

	async def reset_password(self, payload: ResetPasswordRequest) -> None:
		db = get_database()
		token_hash = hashlib.sha256(payload.token.encode("utf-8")).hexdigest()
		record = await db.password_reset_tokens.find_one({"token_hash": token_hash, "used": False})
		if not record:
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token.")

		now_ts = datetime.now(timezone.utc).timestamp()
		if record.get("expires_at", 0) < now_ts:
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token.")

		await db.users.update_one(
			{"_id": record["user_id"]},
			{"$set": {"password_hash": hash_password(payload.new_password), "updated_at": datetime.now(timezone.utc)}},
		)
		await db.password_reset_tokens.update_one({"_id": record["_id"]}, {"$set": {"used": True}})


auth_service = AuthService()