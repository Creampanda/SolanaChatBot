from functools import cached_property
from fastapi import BackgroundTasks, HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session
import logging
from app.services.holder_service import HolderService
from app.services.signature_service import SignatureService
from app.repository.token_repository import TokenRepository
from app.solana.solscan import TokenChainInfo
from app.solana.dexscreener import get_token_info_from_dex
from app import get_db
from app.models.token import Token, TokenData, TokenInfo

logger = logging.getLogger("resources")


class TokenService:
    """
    Service class for managing operations related to tokens.

    Attributes:
        db (Session): The SQLAlchemy database session.
    """

    def __init__(self, db: Session):
        """
        Initializes the TokenService with a database session.

        Args:
            db (Session): The SQLAlchemy database session.
        """
        self.db = db

    @cached_property
    def token_repository(self) -> TokenRepository:
        """
        Lazy-loaded cached property to get the token repository.

        Returns:
            TokenRepository: The token repository instance.
        """
        return TokenRepository(self.db)

    def get_update_authority(self, token_address: str) -> Token:
        """
        Get the update authority for a token.

        Args:
            token_address (str): The address of the token.

        Returns:
            Token: The token object with updated authority.

        Raises:
            HTTPException: If token is not found or an error occurs during update.
        """
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
        """
        Get the deployment transaction for a token.

        Args:
            tci (TokenChainInfo): The TokenChainInfo instance.
            token (Token): The token object.

        Returns:
            Token: The token object with updated deployment transaction.

        Raises:
            HTTPException: If an error occurs during retrieval.
        """
        token.initial_sig = str(tci.find_deploy_transaction())
        self.token_repository.db.commit()
        return token

    def check_if_token(self, token_address: str):
        """
        Check if the provided address is a token address.

        Args:
            token_address (str): The address to be checked.

        Raises:
            HTTPException: If the address is not a token address.
        """
        tci = TokenChainInfo(token_address)
        is_token, msg = tci.check_if_token()
        if not is_token:
            logger.error(str(msg))
            raise HTTPException(status_code=404, detail=str(msg))

    def add_new_token(self, token_address: str, background_tasks: BackgroundTasks) -> TokenInfo:
        """
        Add a new token to the database.

        Args:
            token_address (str): The address of the token.
            background_tasks (BackgroundTasks): BackgroundTasks instance for scheduling tasks.

        Returns:
            TokenInfo: The token information.

        Raises:
            HTTPException: If the token is not found or an error occurs during addition.
        """
        logger.info("Adding new token to the database")
        token = self.token_repository.get_or_none(token_address)
        if token is None:
            self.check_if_token(token_address)
            token = self.token_repository.add_token(token_address)
            # Schedule the collect_token_info to run in the background
            background_tasks.add_task(self.get_update_authority, token_address)
            background_tasks.add_task(SignatureService(db=next(get_db())).collect_signatures, token_address)
            background_tasks.add_task(HolderService(db=next(get_db())).collect_holders, token_address)
        return token

    def get_token_info(self, token_address: str) -> TokenData:
        """
        Get information about a token.

        Args:
            token_address (str): The address of the token.

        Returns:
            TokenData: The token data.

        Raises:
            ValidationError: If there is an error parsing token data.
        """
        data = get_token_info_from_dex(token_address)
        try:
            # Parse the JSON response into the Pydantic model
            token_data = TokenData(**data)
            return token_data
        except ValidationError as e:
            # Handle validation errors
            print(f"Error parsing token data: {str(e)}")
            raise
