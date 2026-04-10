from fastapi import APIRouter, Depends

from app.services.auth.dependencies import get_current_user_optional
from app.services.auth.schema import AuthUser
from app.services.history.service import history_service
from app.services.rewriter.schema import RewriteRequest, RewriteResponse
from app.services.rewriter.service import rewriter_service

router = APIRouter(prefix="/rewriter", tags=["Rewriter"])


@router.post("/rewrite", response_model=RewriteResponse)
async def rewrite_text(payload: RewriteRequest, current_user: AuthUser | None = Depends(get_current_user_optional)) -> RewriteResponse:
	result = await rewriter_service.rewrite(payload)
	if current_user is not None:
		await history_service.record_action(
			user_id=current_user.id,
			username=current_user.username,
			tool="rewriter",
			input_text=payload.text,
			output_text=result.rewritten_text,
			metadata={
				"tone": payload.tone,
				"creativity": payload.creativity,
				"output_format": payload.output_format,
				"purpose": payload.purpose,
			},
		)
	return result
