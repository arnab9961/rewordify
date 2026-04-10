from typing import Literal

from pydantic import BaseModel, Field


class ParaphraseRequest(BaseModel):
	text: str = Field(..., min_length=1, max_length=12000)
	mode: Literal["standard", "fluency", "formal", "simple", "creative"] = Field(default="standard")
	preserve_meaning: bool = Field(default=True)


class ParaphraseResponse(BaseModel):
	paraphrased_text: str
