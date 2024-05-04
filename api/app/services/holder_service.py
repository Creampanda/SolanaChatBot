from sqlalchemy.orm import Session
from fastapi import Depends
from app import get_db
from app.models.holder import Holder, HolderModel  # Ensure your Pydantic model import is correct


class HolderService:
    pass


# Dependency
def get_holder_service(db: Session = Depends(get_db)):
    return HolderService(db)
