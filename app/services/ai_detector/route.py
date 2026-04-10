from fastapi import APIRouter, Depends

from app.services.auth.dependencies import get_current_user_optional
from app.services.auth.schema import AuthUser
from app.services.history.service import history_service
from app.services.ai_detector.schema import AIDetectorRequest, AIDetectorResponse
from app.services.ai_detector.service import ai_detector_service

router = APIRouter(prefix="/ai-detector", tags=["AI Detector"])


@router.post("", response_model=AIDetectorResponse)
async def detect_ai(payload: AIDetectorRequest, current_user: AuthUser | None = Depends(get_current_user_optional)) -> AIDetectorResponse:
	result = await ai_detector_service.detect(payload)
	if current_user is not None:
		await history_service.record_action(
			user_id=current_user.id,
			username=current_user.username,
			tool="ai-detector",
			input_text=payload.text,
			output_text=result.summary,
			metadata={"ai_score": result.ai_score, "human_score": result.human_score, "verdict": result.verdict},
		)
	return result
