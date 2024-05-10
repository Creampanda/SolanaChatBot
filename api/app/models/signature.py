from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app import Base


class Signature(Base):
    """
    SQLAlchemy model representing a signature.

    Attributes:
        signature (str): The signature value.
        slot (int): The slot number.
        block_time (int): The time of the block.
        token_id (int): The ID of the token associated with the signature.
    """

    __tablename__ = "signature"
    signature = Column(String, primary_key=True)
    slot = Column(Integer, nullable=False)
    block_time = Column(Integer, nullable=False)
    token_id = Column(Integer, ForeignKey("token.id"), nullable=False)
    token = relationship("Token", back_populates="signatures")


class SignatureModel(BaseModel):
    """
    Pydantic model representing a signature.

    Attributes:
        signature (str): The signature value.
        slot (int): The slot number.
        block_time (int): The time of the block.
        token_id (int): The ID of the token associated with the signature.
    """

    signature: str
    slot: int
    block_time: int
    token_id: int

    class Config:
        from_attributes = True
