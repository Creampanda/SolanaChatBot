from functools import cached_property
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from api.app.repository.token_repository import get_token_repository
from app.solana.solscan import TokenChainInfo
from app.solana.dexscreener import get_token_info
from app import get_db
from app.models.token import Token, TokenInfo, TokenModel


class TokenService:
    @cached_property
    def token_resp(self):
        return get_token_repository()

    def get_token_info(self, token_address: str) -> TokenInfo:
        """Retrieve token information using an external API call."""
        token_data = get_token_info(token_address)
        if not token_data:
            raise HTTPException(status_code=404, detail="Token information not found.")
        return TokenInfo(address=token_address)
    
    def get_update_authority(self, token_address: str) -> TokenModel:
        token = self.token_resp.get_or_404(token_address)
        tci = TokenChainInfo(token_address)
        token.update_authority = tci.get_token_update_authority()

    def get_collect_token_info(self, token_address: str):
        tci = TokenChainInfo(token_address)
        tci.get_token_update_authority()
        tci.



# Dependency function if no db is needed
def get_token_service():
    return TokenService()
