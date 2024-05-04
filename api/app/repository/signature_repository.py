from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from app import get_db
from app.models.token import Token
from app.models.signature import Signature, SignatureModel


class SignatureRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_signature(self, signature_data: SignatureModel):
        """Add a new signature to the database."""
        new_signature = Signature(
            signature=signature_data.signature,
            slot=signature_data.slot,
            block_time=signature_data.block_time,
            token_id=signature_data.token_id,
        )
        self.db.add(new_signature)
        self.db.commit()
        self.db.refresh(new_signature)
        return new_signature
