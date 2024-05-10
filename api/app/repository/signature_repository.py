from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.signature import Signature
from sqlalchemy.exc import IntegrityError


class SignatureRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_signature(self, new_signature: Signature):
        """Add a new signature to the database."""
        self.db.add(new_signature)
        try:
            self.db.commit()
            self.db.refresh(new_signature)
            return new_signature
        except IntegrityError:
            self.db.rollback()  # Handle duplicate signature insertion etc.
            raise HTTPException(status_code=400, detail="Integrity error on signature insertion.")

    def add_signatures(self, signatures: list[Signature]):
        """Add multiple new signatures to the database using batch insertion."""

        self.db.bulk_save_objects(signatures)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()  # Handle duplicate signature insertion etc.
            raise HTTPException(status_code=400, detail="Integrity error on signature insertion.")
        return signatures
