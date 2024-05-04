from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.repository.token_repository import get_token_repository
from app.services.token_service import get_token_service
from app import get_db
from app.models.token import Token, TokenInfo, TokenModel

router = APIRouter()


@router.get("/get_token_info/{address}", response_model=TokenModel)
async def get_token_info(address: str, db: Session = Depends(get_db)) -> TokenModel:
    token_service = get_token_service()
    token_rep = get_token_repository(db)
    token = token_rep.get_or_404(address)
    return token_service.get_token_info(token.address)


@router.post("/add_token/{address}", response_model=TokenInfo)
async def add_token(address: str, db: Session = Depends(get_db)) -> TokenInfo:
    token_service = get_token_service()
    token_rep = get_token_repository(db)
    token = token_rep.add_token(address)
    return token_service.get_token_info(token.address)


@router.post("/collect_token_signatures/{address}", response_model=TokenModel)
async def collect_token_signatures(address: str, db: Session = Depends(get_db)) -> None:
    # Запрос к базе данных для получения информации о токене по адресу
    token_info = db.query(Token).filter(Token.address == address).first()
    if not token_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Token with address {address} not found."
        )
    return token_info
