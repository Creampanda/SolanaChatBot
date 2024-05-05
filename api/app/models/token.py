from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app import Base


class Token(Base):
    __tablename__ = "token"
    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String, nullable=False, unique=True)
    initial_sig = Column(String, nullable=True)
    update_authority = Column(String, nullable=True)
    signatures = relationship("Signature", back_populates="token")
    holders = relationship("Holder", back_populates="token")


# Pydantic models for response
class TokenModel(BaseModel):
    id: int
    address: str
    initial_sig: str = None
    update_authority: str = None

    class Config:
        from_attributes = True


# Pydantic models for response
class TokenInfo(BaseModel):
    address: str
