import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repository.signature_repository import SignatureRepository
from app.solana.solscan import TokenChainInfo
from app.models.signature import Signature
from app.models.token import Token

logger = logging.getLogger("resources")


class SignatureService:
    """
    Service class for managing operations related to signatures.

    Attributes:
        db (Session): The SQLAlchemy database session.
        signature_repository (SignatureRepository): The repository for signature-related operations.
    """

    def __init__(self, db: Session):
        """
        Initializes the SignatureService with a database session.

        Args:
            db (Session): The SQLAlchemy database session.
        """
        self.db = db
        self.signature_repository = SignatureRepository(db)

    def collect_signatures(self, token_address: str):
        """
        Collect signatures and store them in the database in batches.

        Args:
            token_address (str): The address of the token.

        Raises:
            HTTPException: If token is not found.
        """
        token = self.db.query(Token).filter(Token.address == token_address).first()
        if not token:
            logger.error("Token not found")
            raise HTTPException(status_code=404, detail="Token not found.")
        tci = TokenChainInfo(token_address)
        current_batch = []
        logger.info(f"Collecting signatures for {token.id} {token.address}")
        for signatures_batch in tci.collect_token_signatures():
            for signature in signatures_batch:
                sig_model = Signature(
                    signature=str(signature.signature),
                    slot=int(signature.slot),
                    block_time=int(signature.block_time),
                    token_id=token.id,  # Assuming this is already known
                )
                current_batch.append(sig_model)
                self.signature_repository.add_signatures(current_batch)
                current_batch = []

        if current_batch:
            self.signature_repository.add_signatures(current_batch)
