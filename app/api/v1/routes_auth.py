import io
import pyotp
import qrcode
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse
from passlib.context import CryptContext
from app.db.session import DBSession
from app.models.user import User
from app.schemas.user import Login2faResponse, LoginRequest, LoginResponse
from app.services.user_service import authenticate_user_with_2fa, create_access_token

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
get_db = DBSession.get_db


@router.post("/login/2fa", response_model=Login2faResponse)
def login_2fa(request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user_with_2fa(db, request.username, request.password, request.otp_code)
    if not user:
        raise HTTPException(status_code=400, detail="Credenciais inválidas")

    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "Bearer"}


@router.post("/enable-2fa/{user_id}")
def enable_2fa(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    user.secret_key = pyotp.random_base32()
    user.is_2fa_enabled = True
    db.commit()

    return {"success": True}


@router.get("/qr-code/{user_id}")
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


@router.post("/login", response_model=LoginResponse)
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
