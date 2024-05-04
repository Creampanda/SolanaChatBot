from sqlalchemy.orm import Session
from fastapi import Depends
from app import get_db
from app.models.signature import Signature, SignatureModel


class SignatureService:
    def collect_singatures(self, token_address: str, initial_signature: str):
        pass


# Dependency
def get_signature_service(db: Session = Depends(get_db)):
    return SignatureService(db)
