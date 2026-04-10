from fastapi import APIRouter, Depends, Response

from app.core.config import settings
from app.core.security import create_access_token
from app.services.auth.dependencies import get_current_user
from app.services.auth.schema import (
	AuthUser,
	ForgotPasswordRequest,
	LoginRequest,
	ProfileResponse,
	ResetPasswordRequest,
	SignupRequest,
	VerifySignupOtpRequest,
)
from app.services.auth.service import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


def _set_auth_cookie(response: Response, token: str) -> None:
	response.set_cookie(
		key=settings.auth_cookie_name,
		value=token,
		httponly=True,
		secure=settings.cookie_secure,
		samesite="lax",
		max_age=settings.access_token_expire_minutes * 60,
		path="/",
	)


@router.post("/signup")
async def signup(payload: SignupRequest) -> dict[str, str]:
	await auth_service.create_signup_otp(payload)
	return {"detail": "OTP sent to your email. Verify to complete signup."}


@router.post("/verify-signup", response_model=AuthUser)
async def verify_signup(payload: VerifySignupOtpRequest, response: Response) -> AuthUser:
	user = await auth_service.verify_signup_otp(payload)
	_set_auth_cookie(response, create_access_token(user.id))
	return user


@router.post("/login", response_model=AuthUser)
async def login(payload: LoginRequest, response: Response) -> AuthUser:
	user = await auth_service.authenticate(payload)
	_set_auth_cookie(response, create_access_token(user.id))
	return user


@router.post("/logout")
async def logout(response: Response) -> dict[str, str]:
	response.delete_cookie(settings.auth_cookie_name, path="/")
	return {"detail": "Logged out successfully."}


@router.get("/me", response_model=ProfileResponse)
async def me(current_user: AuthUser = Depends(get_current_user)) -> ProfileResponse:
	return await auth_service.build_profile(current_user.id)


@router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest) -> dict[str, str]:
	await auth_service.request_password_reset(payload)
	return {"detail": "If this email exists, a reset link has been sent."}


@router.post("/reset-password")
async def reset_password(payload: ResetPasswordRequest) -> dict[str, str]:
	await auth_service.reset_password(payload)
	return {"detail": "Password reset successful."}