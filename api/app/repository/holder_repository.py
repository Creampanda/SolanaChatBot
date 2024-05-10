import logging
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from app.models.holder import Holder
from app import get_db

logger = logging.getLogger("resources")


class HolderRepository:
    """
    Repository class for handling operations related to holders in the database.

    Attributes:
        db (Session): The SQLAlchemy database session.
    """

    def __init__(self, db: Session):
        """
        Initializes the HolderRepository with a database session.

        Args:
            db (Session): The SQLAlchemy database session.
        """
        self.db = db

    def add_holder(self, new_holder: Holder):
        """
        Add a new holder to the database.

        Args:
            new_holder (Holder): The new holder object to be added to the database.

        Returns:
            Holder: The newly added holder object.

        Raises:
            HTTPException: If an integrity error occurs during insertion.
        """
        self.db.add(new_holder)
        try:
            self.db.commit()
            self.db.refresh(new_holder)
            return new_holder
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Integrity error on signature insertion.")

    def add_holders(self, holders: list[Holder]):
        """
        Add multiple new holders to the database using batch insertion.

        Args:
            holders (List[Holder]): List of holder objects to be added to the database.

        Returns:
            List[Holder]: List of newly added holder objects.

        Raises:
            HTTPException: If an integrity error occurs during insertion.
        """
        self.db.bulk_save_objects(holders)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Integrity error on signature insertion.")
        return holders


# Dependency
def get_token_repository(db: Session = Depends(get_db)) -> HolderRepository:
    """
    Dependency function to get the HolderRepository instance.

    Args:
        db (Session): The SQLAlchemy database session.

    Returns:
        HolderRepository: The HolderRepository instance.
    """
    return HolderRepository(db)
