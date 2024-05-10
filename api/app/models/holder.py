from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import Column, Integer, PrimaryKeyConstraint, String, ForeignKey, TIMESTAMP, BigInteger
from sqlalchemy.orm import relationship
from app import Base


class Holder(Base):
    """
    SQLAlchemy model representing a holder of a token.

    Attributes:
        address (str): The address of the holder.
        token_id (int): The ID of the token.
        initial_balance (int): The initial balance of the holder.
        current_balance (int): The current balance of the holder.
        last_checked (datetime): The timestamp of when the holder was last checked.
    """

    __tablename__ = "holder"
    address = Column(String, nullable=False)
    token_id = Column(Integer, ForeignKey("token.id"), nullable=False)
    initial_balance = Column(BigInteger, nullable=False)
    current_balance = Column(BigInteger, nullable=False)
    last_checked = Column(TIMESTAMP, nullable=False)
    __table_args__ = (PrimaryKeyConstraint("address", "token_id"),)
    token = relationship("Token", back_populates="holders")


class HolderModel(BaseModel):
    """
    Pydantic model representing a holder of a token.

    Attributes:
        address (str): The address of the holder.
        token_id (int): The ID of the token.
        initial_balance (int): The initial balance of the holder.
        current_balance (int): The current balance of the holder.
        last_checked (datetime): The timestamp of when the holder was last checked.
    """

    address: str
    token_id: int
    initial_balance: int
    current_balance: int
    last_checked: datetime

    class Config:
        from_attributes = True
