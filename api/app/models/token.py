from pydantic import BaseModel
from typing import List
from datetime import datetime
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app import Base


class Token(Base):
    """
    SQLAlchemy model representing a token.

    Attributes:
        id (int): The unique identifier for the token.
        address (str): The address of the token.
        update_authority (str): The update authority of the token.
        signatures (relationship): Relationship to Signature model.
        holders (relationship): Relationship to Holder model.
    """

    __tablename__ = "token"
    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String, nullable=False, unique=True)
    update_authority = Column(String, nullable=True)
    signatures = relationship("Signature", back_populates="token")
    holders = relationship("Holder", back_populates="token")


# Pydantic models for response
class TokenModel(BaseModel):
    """
    Pydantic model representing basic token information.

    Attributes:
        address (str): The address of the token.
    """

    address: str

    class Config:
        from_attributes = True


class TokenInfo(BaseModel):
    """
    Pydantic model representing detailed token information.

    Attributes:
        address (str): The address of the token.
        name (str): The name of the token.
        symbol (str): The symbol of the token.
    """

    address: str
    name: str
    symbol: str


class PriceChange(BaseModel):
    """
    Pydantic model representing price changes.

    Attributes:
        m5 (float): Price change over the last 5 minutes.
        h1 (float): Price change over the last hour.
        h6 (float): Price change over the last 6 hours.
        h24 (float): Price change over the last 24 hours.
    """

    m5: float
    h1: float
    h6: float
    h24: float


class Volume(BaseModel):
    """
    Pydantic model representing trading volume.

    Attributes:
        h24 (float): Volume over the last 24 hours.
        h6 (float): Volume over the last 6 hours.
        h1 (float): Volume over the last hour.
        m5 (float): Volume over the last 5 minutes.
    """

    h24: float
    h6: float
    h1: float
    m5: float


class Liquidity(BaseModel):
    """
    Pydantic model representing liquidity information.

    Attributes:
        usd (float): Liquidity in USD.
        base (float): Liquidity in the base token.
        quote (float): Liquidity in the quote token.
    """

    usd: float
    base: float
    quote: float


class Pair(BaseModel):
    """
    Pydantic model representing a token pair.

    Attributes:
        dexId (str): Identifier of the decentralized exchange.
        url (str): URL of the pair.
        pairAddress (str): Address of the pair.
        baseToken (TokenInfo): Information about the base token.
        quoteToken (TokenInfo): Information about the quote token.
        priceUsd (str): Price in USD.
        volume (Volume): Trading volume.
        liquidity (Liquidity): Liquidity information.
        fdv (int): Fully diluted valuation in USD.
        pairCreatedAt (int): Creation timestamp of the pair.
    """

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
        """
        Calculate the age of the pair in days.

        Returns:
            int: The age of the pair in days.
        """
        creation_date = datetime.fromtimestamp(self.pairCreatedAt / 1000)
        return (datetime.now() - creation_date).days


class TokenData(BaseModel):
    """
    Pydantic model representing token data.

    Attributes:
        pairs (List[Pair]): List of token pairs.
    """

    pairs: List[Pair]

    def get_token_info(self):
        """
        Print detailed information about token pairs.

        Prints:
            str: Detailed information about each token pair.
        """
        for pair in self.pairs:
            print(f"Name: {pair.baseToken.name}, Symbol: {pair.baseToken.symbol}")
            print(f"Price USD: {pair.priceUsd}")
            print(f"Volume (24h USD): {pair.volume.h24}")
            print(f"Liquidity (USD): {pair.liquidity.usd}")
            print(f"FDV (USD): {pair.fdv}")
            print(f"Age (days): {pair.age_in_days}")
