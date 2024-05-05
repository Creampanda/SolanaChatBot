from functools import cached_property
from fastapi import BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from app.services.holder_service import HolderService
from app.services.signature_service import SignatureService
from app.repository.token_repository import TokenRepository, get_token_repository
from app.solana.solscan import TokenChainInfo
from app.solana.dexscreener import get_token_info
from app import SessionLocal, get_db
from app.models.token import Token, TokenInfo, TokenModel

logger = logging.getLogger("resources")


class TokenService:
    def __init__(self, db: Session):
        self.db = db

    @cached_property
    def token_repository(self) -> TokenRepository:
        """Lazy-loaded cached property to get the token repository."""
        return TokenRepository(self.db)

    def get_token_info(self, token_address: str) -> TokenInfo:
        """Retrieve token information using an external API call."""
        token_data = get_token_info(token_address)
        if not token_data:
            raise HTTPException(status_code=404, detail="Token information not found.")
        return TokenInfo(address=token_address)

    def get_update_authority(self, token_address: str) -> Token:
        db = get_db()
        try:
            token = self.db.query(Token).filter(Token.address == token_address).first()
            if not token:
                logger.error("Token not found")
                raise HTTPException(status_code=404, detail="Token not found.")
            tci = TokenChainInfo(token.address)
            logger.info(f"Searching update authority for {token.address}...")
            token.update_authority = str(tci.get_token_update_authority())
            logger.info(f"{token.update_authority=}")
            self.token_repository.db.commit()
            self.db.refresh(token)
            return token

        except Exception as e:
            db.rollback()
            logger.error(f"Error updating token: {str(e)}")
        finally:
            db.close()

    def get_deploy_transaction(self, tci: TokenChainInfo, token: Token) -> Token:
        token.initial_sig = str(tci.find_deploy_transaction())
        self.token_repository.db.commit()
        return token

    def add_new_token(self, token_address: str, background_tasks: BackgroundTasks) -> TokenInfo:
        logger.info("Adding new token to the database")
        token = self.token_repository.get_or_none(token_address)
        if token is None:
            token = self.token_repository.add_token(token_address)
            # Schedule the collect_token_info to run in the background
            background_tasks.add_task(self.get_update_authority, token_address)
            background_tasks.add_task(SignatureService(db=next(get_db())).collect_signatures, token_address)
            background_tasks.add_task(HolderService(db=next(get_db())).collect_holders, token_address)
        return token
