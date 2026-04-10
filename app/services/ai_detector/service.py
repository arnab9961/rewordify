import json
import re

import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.services.ai_detector.schema import AIDetectorRequest, AIDetectorResponse


class AIDetectorService:
	def _extract_json(self, text: str) -> dict:
		match = re.search(r"\{.*\}", text, re.DOTALL)
		if not match:
			raise ValueError("No JSON object found")
		return json.loads(match.group(0))

	def _heuristic_fallback(self, text: str) -> AIDetectorResponse:
		sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
		words = re.findall(r"\b\w+\b", text.lower())
		if not words:
			return AIDetectorResponse(ai_score=50, human_score=50, verdict="Uncertain", summary="Insufficient text for analysis.")

		unique_ratio = len(set(words)) / max(len(words), 1)
		avg_sentence_len = (len(words) / max(len(sentences), 1)) if sentences else len(words)

		score = 40
		if unique_ratio < 0.42:
			score += 20
		if avg_sentence_len > 24:
			score += 15
		if re.search(r"\b(in conclusion|overall|furthermore|moreover|therefore)\b", text.lower()):
			score += 15

		ai_score = max(0, min(100, score))
		human_score = 100 - ai_score
		if ai_score >= 70:
			verdict = "Likely AI-generated"
		elif ai_score >= 45:
			verdict = "Mixed signals"
		else:
			verdict = "Likely human-written"

		return AIDetectorResponse(
			ai_score=ai_score,
			human_score=human_score,
			verdict=verdict,
			summary="Fallback heuristic estimate used due to parser/API uncertainty.",
		)

	async def detect(self, payload: AIDetectorRequest) -> AIDetectorResponse:
		request_payload = {
			"model": settings.model,
			"messages": [
				{
					"role": "system",
					"content": (
						"You are a writing forensics assistant. Estimate AI-generated probability for the provided text. "
						"Return only valid JSON with keys: ai_score, verdict, summary. ai_score must be an integer 0-100."
					),
				},
				{"role": "user", "content": f"Analyze this text:\n{payload.text}"},
			],
			"temperature": 0.1,
			"max_tokens": 300,
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
		except httpx.HTTPError:
			return self._heuristic_fallback(payload.text)

		data = response.json()
		choices = data.get("choices", [])
		if not choices:
			return self._heuristic_fallback(payload.text)

		raw_content = choices[0].get("message", {}).get("content", "")
		clean_content = re.sub(r"<think>.*?</think>", "", raw_content, flags=re.IGNORECASE | re.DOTALL).strip()

		try:
			parsed = self._extract_json(clean_content)
			ai_score = int(parsed.get("ai_score", 50))
			ai_score = max(0, min(100, ai_score))
			verdict = str(parsed.get("verdict", "Mixed signals")).strip() or "Mixed signals"
			summary = str(parsed.get("summary", "AI-likelihood estimated from writing patterns.")).strip()
			return AIDetectorResponse(
				ai_score=ai_score,
				human_score=100 - ai_score,
				verdict=verdict,
				summary=summary,
			)
		except (ValueError, TypeError, json.JSONDecodeError):
			return self._heuristic_fallback(payload.text)


ai_detector_service = AIDetectorService()
