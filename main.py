from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.services.ai_detector.route import router as ai_detector_router
from app.services.paraphrase.route import router as paraphrase_router
from app.services.rewriter.route import router as rewriter_router

app = FastAPI(title="ReWordify API", version="1.0.0")
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "app" / "static"

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def landing() -> FileResponse:
	return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
	return {"status": "ok"}


app.include_router(rewriter_router)
app.include_router(paraphrase_router)
app.include_router(ai_detector_router)
