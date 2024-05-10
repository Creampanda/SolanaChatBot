from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.signature import Signature
from sqlalchemy.exc import IntegrityError


class SignatureRepository:
    """
    Repository class for handling operations related to signatures in the database.

    Attributes:
        db (Session): The SQLAlchemy database session.
    """

    def __init__(self, db: Session):
        """
        Initializes the SignatureRepository with a database session.

        Args:
            db (Session): The SQLAlchemy database session.
        """
        self.db = db

    def add_signature(self, new_signature: Signature):
        """
        Add a new signature to the database.

        Args:
            new_signature (Signature): The new signature object to be added to the database.

        Returns:
            Signature: The newly added signature object.

        Raises:
            HTTPException: If an integrity error occurs during insertion.
        """
        self.db.add(new_signature)
        try:
            self.db.commit()
            self.db.refresh(new_signature)
            return new_signature
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Integrity error on signature insertion.")

    def add_signatures(self, signatures: list[Signature]):
        """
        Add multiple new signatures to the database using batch insertion.

        Args:
            signatures (List[Signature]): List of signature objects to be added to the database.

        Returns:
            List[Signature]: List of newly added signature objects.

        Raises:
            HTTPException: If an integrity error occurs during insertion.
        """
        self.db.bulk_save_objects(signatures)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Integrity error on signature insertion.")
        return signatures
