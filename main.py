from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.core.db import close_database, init_database
from app.services.auth.route import router as auth_router
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


@app.on_event("startup")
async def startup() -> None:
	await init_database()


@app.on_event("shutdown")
async def shutdown() -> None:
	await close_database()


@app.get("/")
def landing() -> FileResponse:
	return FileResponse(STATIC_DIR / "index.html")


@app.get("/login")
def login_page() -> FileResponse:
	return FileResponse(STATIC_DIR / "login.html")


@app.get("/signup")
def signup_page() -> FileResponse:
	return FileResponse(STATIC_DIR / "signup.html")


@app.get("/forgot-password")
def forgot_password_page() -> FileResponse:
	return FileResponse(STATIC_DIR / "forgot-password.html")


@app.get("/reset-password")
def reset_password_page() -> FileResponse:
	return FileResponse(STATIC_DIR / "reset-password.html")


@app.get("/history")
def history_page() -> FileResponse:
	return FileResponse(STATIC_DIR / "history.html")


@app.get("/health")
def health() -> dict[str, str]:
	return {"status": "ok"}


app.include_router(rewriter_router)
app.include_router(paraphrase_router)
app.include_router(ai_detector_router)
app.include_router(auth_router)
