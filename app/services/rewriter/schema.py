from typing import Literal

from pydantic import BaseModel, Field


class RewriteRequest(BaseModel):
	text: str = Field(..., min_length=1, max_length=12000, description="Text to rewrite")
	tone: Literal[
		"neutral",
		"professional",
		"friendly",
		"academic",
		"persuasive",
		"casual",
		"concise",
	] = Field(default="neutral")
	creativity: Literal["low", "balanced", "high"] = Field(default="balanced")
	output_format: Literal["paragraph", "bullets"] = Field(default="paragraph")
	audience: str | None = Field(default=None, max_length=120)
	purpose: str | None = Field(default=None, max_length=200)
	preserve_meaning: bool = Field(default=True)


class RewriteResponse(BaseModel):
	rewritten_text: str
	model: str
	tokens_prompt: int | None = None
	tokens_completion: int | None = None
