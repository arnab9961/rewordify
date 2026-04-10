from fastapi import APIRouter

from app.services.rewriter.schema import RewriteRequest, RewriteResponse
from app.services.rewriter.service import rewriter_service

router = APIRouter(prefix="/rewriter", tags=["Rewriter"])


@router.post("/rewrite", response_model=RewriteResponse)
async def rewrite_text(payload: RewriteRequest) -> RewriteResponse:
	return await rewriter_service.rewrite(payload)
