import logging
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from app import get_db
from app.models.token import Token

logger = logging.getLogger("resources")


class TokenRepository:
    """
    Repository class for handling operations related to tokens in the database.

    Attributes:
        db (Session): The SQLAlchemy database session.
    """

    def __init__(self, db: Session = Depends(get_db)):
        """
        Initializes the TokenRepository with a database session.

        Args:
            db (Session): The SQLAlchemy database session.
        """
        self.db = db

    def add_token(self, address: str):
        """
        Add a new token to the database or return an existing token.

        Args:
            address (str): The address of the token.

        Returns:
            Token: The newly created or existing token.

        Raises:
            HTTPException: If failed to create token due to integrity error.
        """
        existing_token = self.db.query(Token).filter_by(address=address).first()
        if existing_token:
            return existing_token

        try:
            new_token = Token(address=address)
            self.db.add(new_token)
            self.db.commit()
            self.db.refresh(new_token)
            return new_token
        except IntegrityError as e:
            self.db.rollback()
            logger.error(str(e))
            raise HTTPException(status_code=400, detail="Failed to create token due to integrity error.")

    def get_or_create_token(self, token_address: str):
        """
        Retrieve a token by address or create it if it does not exist.

        Args:
            token_address (str): The address of the token.

        Returns:
            Token: The retrieved or newly created token.
        """
        token = self.db.query(Token).filter(Token.address == token_address).first()
        if not token:
            token = self.add_token(token_address)
        return token

    def get_or_404(self, token_address: str):
        """
        Retrieve a token by address or raise HTTP 404 if it does not exist.

        Args:
            token_address (str): The address of the token.

        Returns:
            Token: The retrieved token.

        Raises:
            HTTPException: If token with the given address is not found.
        """
        token = self.db.query(Token).filter(Token.address == token_address).first()
        if not token:
            raise HTTPException(status_code=404, detail=f"Token with address {token_address} not found.")
        return token

    def get_or_none(self, token_address: str):
        """
        Retrieve a token by address or return None if it does not exist.

        Args:
            token_address (str): The address of the token.

        Returns:
            Token: The retrieved token or None if not found.
        """
        token = self.db.query(Token).filter(Token.address == token_address).first()
        return token


# Dependency
def get_token_repository(db: Session = Depends(get_db)) -> TokenRepository:
    """
    Dependency function to get the TokenRepository instance.

    Args:
        db (Session): The SQLAlchemy database session.

    Returns:
        TokenRepository: The TokenRepository instance.
    """
    return TokenRepository(db)
