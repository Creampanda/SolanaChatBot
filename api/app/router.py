from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import get_db
from app.models.token import Token, TokenModel

router = APIRouter()


@router.get("/get_token_info/{address}", response_model=TokenModel)
async def get_token_info(address: str, db: Session = Depends(get_db)) -> TokenModel:
    # Запрос к базе данных для получения информации о токене по адресу
    token_info = db.query(Token).filter(Token.address == address).first()
    if not token_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Token with address {address} not found."
        )
    return token_info
