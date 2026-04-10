from fastapi import APIRouter, Depends

from app.services.auth.dependencies import get_current_user_optional
from app.services.auth.schema import AuthUser
from app.services.history.service import history_service
from app.services.paraphrase.schema import ParaphraseRequest, ParaphraseResponse
from app.services.paraphrase.service import paraphrase_service

router = APIRouter(prefix="/paraphrase", tags=["Paraphrase"])


@router.post("", response_model=ParaphraseResponse)
async def paraphrase_text(payload: ParaphraseRequest, current_user: AuthUser | None = Depends(get_current_user_optional)) -> ParaphraseResponse:
	result = await paraphrase_service.paraphrase(payload)
	if current_user is not None:
		await history_service.record_action(
			user_id=current_user.id,
			username=current_user.username,
			tool="paraphrase",
			input_text=payload.text,
			output_text=result.paraphrased_text,
			metadata={"mode": payload.mode, "preserve_meaning": payload.preserve_meaning},
		)
	return result
