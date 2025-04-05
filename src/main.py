import io

import pyotp
import qrcode
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from src.auth import create_access_token, authenticate_user_with_2fa
from src.database import engine, Base, get_db
from src.models import User
from src.schemas import UserResponse, UserCreate, LoginResponse, LoginRequest, Login2faResponse

app = FastAPI()


# Path to frontend dist (relative to src/main.py)
BASE_DIR = Path(__file__).resolve().parent.parent
dist_path = BASE_DIR / "frontend-dist"

# Serve the assets
app.mount("/assets", StaticFiles(directory=dist_path / "assets"), name="assets")
app.mount("/static", StaticFiles(directory=dist_path), name="static")  # opcional (ex: vite.svg)


# Main route returns React's index.html
@app.get("/")
def read_index():
    return FileResponse(dist_path / "index.html")


Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/user/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)) -> UserResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)


@app.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/login/2fa", response_model=Login2faResponse)
def login_2fa(request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user_with_2fa(db, request.username, request.password, request.otp_code)
    if not user:
        raise HTTPException(status_code=400, detail="Credenciais inválidas")

    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "Bearer"}


@app.post("/enable-2fa/{user_id}")
def enable_2fa(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    user.secret_key = pyotp.random_base32()
    user.is_2fa_enabled = True
    db.commit()

    return {"success": True}


@app.get("/qr-code/{user_id}")
def get_qr_code(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.secret_key:
        raise HTTPException(status_code=404, detail="Usuário não tem 2FA")

    totp = pyotp.TOTP(user.secret_key)
    uri = totp.provisioning_uri(name=user.username, issuer_name="2fa-user-authenticator")

    qr = qrcode.make(uri)
    img_io = io.BytesIO()
    qr.save(img_io, "PNG")
    img_io.seek(0)

    return StreamingResponse(img_io, media_type="image/png")


@app.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if not pwd_context.verify(request.password, user.password):
        raise HTTPException(status_code=400, detail="Credenciais inválidas")

    if user.is_2fa_enabled:
        return {
            "requires_2fa": True,
            "user_id": user.id
        }

    access_token = create_access_token({"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "Bearer"
    }


@app.get("/user-by-username/{username}", response_model=UserResponse)
def get_user_by_username(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user
