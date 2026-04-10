from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
	username: str = Field(..., min_length=3, max_length=32)
	email: EmailStr
	password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
	identifier: str = Field(..., min_length=3, max_length=120)
	password: str = Field(..., min_length=1, max_length=128)


class ForgotPasswordRequest(BaseModel):
	email: EmailStr


class ResetPasswordRequest(BaseModel):
	token: str = Field(..., min_length=20, max_length=300)
	new_password: str = Field(..., min_length=8, max_length=128)


class VerifySignupOtpRequest(BaseModel):
	email: EmailStr
	otp: str = Field(..., min_length=4, max_length=10)


class AuthUser(BaseModel):
	id: str
	username: str
	email: EmailStr
	created_at: datetime | None = None


class HistoryItem(BaseModel):
	id: str
	tool: str
	input_text: str
	output_text: str | None = None
	metadata: dict = Field(default_factory=dict)
	created_at: datetime | None = None


class ProfileResponse(BaseModel):
	user: AuthUser
	recent_history: list[HistoryItem]
	total_history: int