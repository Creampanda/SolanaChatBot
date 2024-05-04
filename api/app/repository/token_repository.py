from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from app import get_db
from app.models.token import Token


class TokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_token(self, address: str):
        """Check if a token exists and return it; otherwise, create a new token."""
        # Check if the token already exists
        existing_token = self.db.query(Token).filter_by(address=address).first()
        if existing_token:
            return existing_token  # Return the existing token if found

        # If not found, create a new token
        try:
            new_token = Token(address=address)
            self.db.add(new_token)
            self.db.commit()
            self.db.refresh(new_token)  # Refresh to get the newly created token from the database
            return new_token
        except IntegrityError as e:
            self.db.rollback()  # Rollback in case of any errors during insertion
            raise HTTPException(status_code=400, detail="Failed to create token due to integrity error.")

    def get_or_create_token(self, token_address: str):
        """Retrieve a token by address or create it if it does not exist."""
        token = self.db.query(Token).filter(Token.address == token_address).first()
        if not token:
            # Token does not exist, so create a new one
            token = self.add_token(token_address)
        return token

    def get_or_404(self, token_address: str):
        """Retrieve a token by address or raise HTTP 404 if it does not exist."""
        token = self.db.query(Token).filter(Token.address == token_address).first()
        if not token:
            raise HTTPException(status_code=404, detail=f"Token with address {token_address} not found.")
        return token


# Dependency
def get_token_repository(db: Session = Depends(get_db)) -> TokenRepository:
    return TokenRepository(db)
