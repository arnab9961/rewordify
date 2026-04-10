import re

import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.services.paraphrase.schema import ParaphraseRequest, ParaphraseResponse


class ParaphraseService:
	def _sanitize_text(self, text: str) -> str:
		cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.IGNORECASE | re.DOTALL)
		cleaned = re.sub(r"^\s*(paraphrased text|final answer|answer)\s*:\s*", "", cleaned, flags=re.IGNORECASE)
		cleaned = cleaned.replace("```", "")
		return cleaned.strip()

	def _build_messages(self, payload: ParaphraseRequest) -> list[dict[str, str]]:
		system_prompt = (
			"You are an expert paraphrasing assistant. Rephrase the given text with improved readability "
			"and flow while preserving core meaning and facts. Return only the paraphrased text."
		)

		user_prompt = (
			"Paraphrase the following text.\n"
			f"- Mode: {payload.mode}\n"
			f"- Preserve original meaning: {payload.preserve_meaning}\n\n"
			f"Text:\n{payload.text}"
		)
		return [
			{"role": "system", "content": system_prompt},
			{"role": "user", "content": user_prompt},
		]

	async def paraphrase(self, payload: ParaphraseRequest) -> ParaphraseResponse:
		request_payload = {
			"model": settings.model,
			"messages": self._build_messages(payload),
			"temperature": settings.model_temperature,
			"max_tokens": settings.model_max_tokens,
		}
		headers = {
			"Authorization": f"Bearer {settings.groq_cloud_api_key}",
			"Content-Type": "application/json",
		}

		try:
			async with httpx.AsyncClient(timeout=45.0) as client:
				response = await client.post(f"{settings.groq_base_url}/chat/completions", headers=headers, json=request_payload)
			response.raise_for_status()
		except httpx.HTTPStatusError as exc:
			detail = exc.response.text if exc.response is not None else "Model request failed"
			raise HTTPException(status_code=502, detail=f"Groq API error: {detail}") from exc
		except httpx.HTTPError as exc:
			raise HTTPException(status_code=502, detail=f"Network error: {exc}") from exc

		data = response.json()
		choices = data.get("choices", [])
		if not choices:
			raise HTTPException(status_code=502, detail="No response choices returned by model")

		paraphrased_text = self._sanitize_text(choices[0].get("message", {}).get("content", ""))
		if not paraphrased_text:
			raise HTTPException(status_code=502, detail="Model returned an empty paraphrase")

		return ParaphraseResponse(paraphrased_text=paraphrased_text)


paraphrase_service = ParaphraseService()
