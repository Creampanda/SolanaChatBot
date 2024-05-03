from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import Column, Integer, PrimaryKeyConstraint, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app import Base


class Holder(Base):
    __tablename__ = "holder"
    address = Column(String, nullable=False)
    token_id = Column(Integer, ForeignKey("token.id"), nullable=False)
    initial_balance = Column(Integer, nullable=False)
    current_balance = Column(Integer, nullable=False)
    last_checked = Column(TIMESTAMP, nullable=False)
    __table_args__ = (PrimaryKeyConstraint("address", "token_id"),)
    token = relationship("Token", back_populates="holders")


class HolderModel(BaseModel):
    address: str
    token_id: int
    initial_balance: int
    current_balance: int
    last_checked: datetime

    class Config:
        orm_mode = True
