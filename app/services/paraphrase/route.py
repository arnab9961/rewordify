from fastapi import APIRouter

from app.services.paraphrase.schema import ParaphraseRequest, ParaphraseResponse
from app.services.paraphrase.service import paraphrase_service

router = APIRouter(prefix="/paraphrase", tags=["Paraphrase"])


@router.post("", response_model=ParaphraseResponse)
async def paraphrase_text(payload: ParaphraseRequest) -> ParaphraseResponse:
	return await paraphrase_service.paraphrase(payload)
