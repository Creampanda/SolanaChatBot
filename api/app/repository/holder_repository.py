import logging
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from app.models.holder import Holder
from app import get_db

logger = logging.getLogger("resources")


class HolderRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_holder(self, new_holder: Holder):
        """Add a new holder to the database."""
        self.db.add(new_holder)
        try:
            self.db.commit()
            self.db.refresh(new_holder)
            return new_holder
        except IntegrityError:
            self.db.rollback()  # Handle duplicate signature insertion etc.
            raise HTTPException(status_code=400, detail="Integrity error on signature insertion.")

    def add_holders(self, holders: list[Holder]):
        """Add multiple new holders to the database using batch insertion."""

        self.db.bulk_save_objects(holders)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()  # Handle duplicate signature insertion etc.
            raise HTTPException(status_code=400, detail="Integrity error on signature insertion.")
        return holders


# Dependency
def get_token_repository(db: Session = Depends(get_db)) -> HolderRepository:
    return HolderRepository(db)
