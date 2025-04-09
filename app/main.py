from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
from pathlib import Path
from app.db.database import Base, engine
from app.api.v1.routes_auth import router as auth_router
from app.api.v1.routes_user import router as user_router

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
dist_path = BASE_DIR / "frontend" / "dist"

# Static and frontend
app.mount("/assets", StaticFiles(directory=dist_path / "assets"), name="assets")
app.mount("/static", StaticFiles(directory=dist_path), name="static")


@app.get("/")
def read_index():
    return FileResponse(dist_path / "index.html")


# Database
Base.metadata.create_all(bind=engine)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(user_router)
app.include_router(auth_router)
