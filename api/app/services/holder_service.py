import logging
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from app.solana.solscan import TokenChainInfo
from app.repository.holder_repository import HolderRepository
from app import get_db
from app.models.holder import Holder, HolderModel  # Ensure your Pydantic model import is correct
from app.models.token import Token
from app.models.signature import Signature

logger = logging.getLogger("resources")


class HolderService:
    def __init__(self, db: Session):
        self.db = db
        self.holder_repository = HolderRepository(db)

    def collect_holders(self, token_address):
        """Collect signatures and store them in the database in batches."""
        token = self.db.query(Token).filter(Token.address == token_address).first()
        if not token:
            logger.error("Token not found")
            raise HTTPException(status_code=404, detail="Token not found.")
        signatures = (
            self.db.query(Signature)
            .filter(Signature.token_id == token.id)
            .order_by(Signature.slot.asc())
            .all()
        )
        tci = TokenChainInfo(token_address)
        logger.info(f"Collecting holders for {token.id} {token.address}")
        signatures = [signature.signature for signature in signatures]
        unique_holders = tci.find_first_50_transactions(signatures=signatures)
        last_checked = datetime.now()
        for pk, amount in unique_holders.items():
            holder_address = str(pk)
            holder = Holder(
                address=holder_address,
                token_id=token.id,
                initial_balance=amount,
                current_balance=amount,
                last_checked=last_checked,
            )
            self.holder_repository.add_holder(holder)

    def update_holders_info(self, token_address) -> List[HolderModel]:
        token = self.db.query(Token).filter(Token.address == token_address).first()
        if not token:
            logger.error("Token not found")
            raise HTTPException(status_code=404, detail="Token not found.")
        holders = self.db.query(Holder).filter(Holder.token_id == token.id).all()
        if not holders:
            logger.error(f"No holders found for token {token.address}")
            raise HTTPException(status_code=404, detail="Holders not found.")
        tci = TokenChainInfo(token_address)
        logger.info(f"Collecting holders for {token.id} {token.address}")
        holders_addresses = [holder.address for holder in holders]
        current_balances = tci.get_current_holders_balances(holders_addresses)
        last_checked = datetime.now()
        for holder, current_balance in zip(holders, current_balances):
            holder.current_balance = current_balance
            holder.last_checked = last_checked
        try:
            self.db.commit()
            logger.info(f"Updated holders information for token {token.address}")
        except Exception as e:
            logger.error(f"Failed to update holders: {str(e)}")
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to update holder information")
        return holders


# Dependency
def get_holder_service(db: Session = Depends(get_db)):
    return HolderService(db)
