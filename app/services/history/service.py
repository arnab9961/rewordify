from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId

from app.core.db import get_database


class HistoryService:
	async def record_action(
		self,
		user_id: str,
		username: str,
		tool: str,
		input_text: str,
		output_text: str | None,
		metadata: dict | None = None,
	) -> None:
		db = get_database()
		try:
			object_id = ObjectId(user_id)
		except (InvalidId, TypeError):
			return
		await db.history.insert_one(
			{
				"user_id": object_id,
				"username": username,
				"tool": tool,
				"input_text": input_text,
				"output_text": output_text,
				"metadata": metadata or {},
				"created_at": datetime.now(timezone.utc),
			}
		)

	async def get_recent_history(self, user_id: str, limit: int = 10) -> list[dict]:
		db = get_database()
		try:
			object_id = ObjectId(user_id)
		except (InvalidId, TypeError):
			return []
		cursor = db.history.find({"user_id": object_id}).sort("created_at", -1).limit(limit)
		items: list[dict] = []
		async for item in cursor:
			items.append(
				{
					"id": str(item["_id"]),
					"tool": item.get("tool"),
					"input_text": item.get("input_text", ""),
					"output_text": item.get("output_text", ""),
					"metadata": item.get("metadata", {}),
					"created_at": item.get("created_at"),
				}
			)
		return items

	async def get_history_count(self, user_id: str) -> int:
		db = get_database()
		try:
			object_id = ObjectId(user_id)
		except (InvalidId, TypeError):
			return 0
		return await db.history.count_documents({"user_id": object_id})


history_service = HistoryService()