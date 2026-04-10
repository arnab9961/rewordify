import re

import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.services.rewriter.schema import RewriteRequest, RewriteResponse


class RewriterService:
	def _sanitize_rewritten_text(self, text: str) -> str:
		# Remove reasoning blocks and common wrapper labels if a model leaks them.
		cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.IGNORECASE | re.DOTALL)
		cleaned = re.sub(r"^\s*(final answer|rewritten result|answer)\s*:\s*", "", cleaned, flags=re.IGNORECASE)
		cleaned = cleaned.replace("```", "")
		return cleaned.strip()

	def _temperature_from_creativity(self, creativity: str) -> float:
		if creativity == "low":
			return max(0.05, min(settings.model_temperature, 0.25))
		if creativity == "high":
			return min(0.95, max(settings.model_temperature, 0.75))
		return settings.model_temperature

	def _build_messages(self, payload: RewriteRequest) -> list[dict[str, str]]:
		system_prompt = (
			"You are an elite rewriting assistant. Improve clarity, grammar, rhythm, and style while "
			"preserving core meaning and factual content. Avoid adding unsupported claims. "
			"Return only the rewritten text, with no preface."
		)

		instructions = [
			f"Tone: {payload.tone}",
			f"Output format: {payload.output_format}",
			f"Preserve original meaning: {payload.preserve_meaning}",
		]
		if payload.audience:
			instructions.append(f"Target audience: {payload.audience}")
		if payload.purpose:
			instructions.append(f"Purpose: {payload.purpose}")

		user_prompt = (
			"Rewrite the text below using these requirements:\n"
			f"- {'\n- '.join(instructions)}\n\n"
			f"Original text:\n{payload.text}"
		)

		return [
			{"role": "system", "content": system_prompt},
			{"role": "user", "content": user_prompt},
		]

	async def rewrite(self, payload: RewriteRequest) -> RewriteResponse:
		temperature = self._temperature_from_creativity(payload.creativity)
		url = f"{settings.groq_base_url}/chat/completions"
		request_payload = {
			"model": settings.model,
			"messages": self._build_messages(payload),
			"temperature": temperature,
			"max_tokens": settings.model_max_tokens,
		}

		headers = {
			"Authorization": f"Bearer {settings.groq_cloud_api_key}",
			"Content-Type": "application/json",
		}

		try:
			async with httpx.AsyncClient(timeout=45.0) as client:
				response = await client.post(url, headers=headers, json=request_payload)
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

		rewritten_text = self._sanitize_rewritten_text(choices[0].get("message", {}).get("content", ""))
		if not rewritten_text:
			raise HTTPException(status_code=502, detail="Model returned an empty rewrite")

		usage = data.get("usage", {})
		return RewriteResponse(
			rewritten_text=rewritten_text,
			model=settings.model,
			tokens_prompt=usage.get("prompt_tokens"),
			tokens_completion=usage.get("completion_tokens"),
		)


rewriter_service = RewriterService()
