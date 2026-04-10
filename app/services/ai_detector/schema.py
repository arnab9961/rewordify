from pydantic import BaseModel, Field


class AIDetectorRequest(BaseModel):
	text: str = Field(..., min_length=1, max_length=12000)


class AIDetectorResponse(BaseModel):
	ai_score: int = Field(..., ge=0, le=100)
	human_score: int = Field(..., ge=0, le=100)
	verdict: str
	summary: str
