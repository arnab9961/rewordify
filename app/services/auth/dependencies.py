from fastapi import Cookie, HTTPException, status
from jose import JWTError

from app.core.config import settings
from app.core.security import decode_access_token
from app.services.auth.schema import AuthUser
from app.services.auth.service import auth_service


async def get_current_user_optional(access_token: str | None = Cookie(default=None, alias=settings.auth_cookie_name)) -> AuthUser | None:
	if not access_token:
		return None
	try:
		payload = decode_access_token(access_token)
	except JWTError:
		return None
	user_id = payload.get("sub")
	if not user_id:
		return None
	return await auth_service.get_user_by_id(user_id)


async def get_current_user(access_token: str | None = Cookie(default=None, alias=settings.auth_cookie_name)) -> AuthUser:
	user = await get_current_user_optional(access_token)
	if user is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")
	return user