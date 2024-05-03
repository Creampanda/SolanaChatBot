from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from app import Base


class Token(Base):
    __tablename__ = "token"
    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String, nullable=False, unique=True)

# Pydantic models for response
class TokenModel(BaseModel):
    id: int
    address: str

    class Config:
        orm_mode = True

