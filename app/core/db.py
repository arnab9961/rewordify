from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
	global _client
	if _client is None:
		_client = AsyncIOMotorClient(settings.mongodb_url)
	return _client


def get_database() -> AsyncIOMotorDatabase:
	return get_client()[settings.mongodb_db_name]


async def init_database() -> None:
	db = get_database()
	await db.users.create_index("username", unique=True)
	await db.users.create_index("email", unique=True)
	await db.history.create_index([("user_id", 1), ("created_at", -1)])
	await db.signup_otps.create_index("email", unique=True)
	await db.signup_otps.create_index("username", unique=True)
	await db.signup_otps.create_index("created_at", expireAfterSeconds=60 * 60 * 24)
	await db.password_reset_tokens.create_index("token_hash", unique=True)
	await db.password_reset_tokens.create_index("created_at", expireAfterSeconds=60 * 60 * 24)


async def close_database() -> None:
	global _client
	if _client is not None:
		_client.close()
		_client = None