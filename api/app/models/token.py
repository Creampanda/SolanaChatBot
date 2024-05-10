from pydantic import BaseModel
from typing import List
from datetime import datetime
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app import Base


class Token(Base):
    __tablename__ = "token"
    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String, nullable=False, unique=True)
    update_authority = Column(String, nullable=True)
    signatures = relationship("Signature", back_populates="token")
    holders = relationship("Holder", back_populates="token")


# Pydantic models for response
class TokenModel(BaseModel):
    address: str

    class Config:
        from_attributes = True


class TokenInfo(BaseModel):
    address: str
    name: str
    symbol: str


class PriceChange(BaseModel):
    m5: float
    h1: float
    h6: float
    h24: float


class Volume(BaseModel):
    h24: float
    h6: float
    h1: float
    m5: float


class Liquidity(BaseModel):
    usd: float
    base: float
    quote: float


class Pair(BaseModel):
    dexId: str
    url: str
    pairAddress: str
    baseToken: TokenInfo
    quoteToken: TokenInfo
    priceUsd: str
    volume: Volume
    liquidity: Liquidity
    fdv: int
    pairCreatedAt: int

    @property
    def age_in_days(self) -> int:
        creation_date = datetime.fromtimestamp(self.pairCreatedAt / 1000)
        return (datetime.now() - creation_date).days


class TokenData(BaseModel):
    pairs: List[Pair]

    def get_token_info(self):
        for pair in self.pairs:
            print(f"Name: {pair.baseToken.name}, Symbol: {pair.baseToken.symbol}")
            print(f"Price USD: {pair.priceUsd}")
            print(f"Volume (24h USD): {pair.volume.h24}")
            print(f"Liquidity (USD): {pair.liquidity.usd}")
            print(f"FDV (USD): {pair.fdv}")
            print(f"Age (days): {pair.age_in_days}")
