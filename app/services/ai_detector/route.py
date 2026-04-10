from fastapi import APIRouter

from app.services.ai_detector.schema import AIDetectorRequest, AIDetectorResponse
from app.services.ai_detector.service import ai_detector_service

router = APIRouter(prefix="/ai-detector", tags=["AI Detector"])


@router.post("", response_model=AIDetectorResponse)
async def detect_ai(payload: AIDetectorRequest) -> AIDetectorResponse:
	return await ai_detector_service.detect(payload)
