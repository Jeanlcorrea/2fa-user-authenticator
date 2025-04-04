from sqlalchemy import Column, Integer, String, Boolean

from src.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    secret_key = Column(String, nullable=True)
    is_2fa_enabled = Column(Boolean, default=False)
