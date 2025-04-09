from typing import Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    is_2fa_enabled: bool

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str
    otp_code: str | None = None  # Optional for those who have not activated 2FA


class LoginResponse(BaseModel):
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    requires_2fa: Optional[bool] = None
    user_id: Optional[int] = None


class Login2faResponse(BaseModel):
    access_token: str
    token_type: str

