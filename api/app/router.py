from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.holder import HolderModel
from app.services.holder_service import HolderService
from app.repository.token_repository import get_token_repository
from app.services.token_service import TokenService
from app import get_db
from app.models.token import Token, TokenData, TokenInfo, TokenModel

router = APIRouter()


@router.get("/get_token_info/{address}", response_model=TokenData)
async def get_token_info(address: str, db: Session = Depends(get_db)) -> TokenData:
    token_service = TokenService(db)
    token_rep = get_token_repository(db)
    token = token_rep.get_or_404(address)
    return token_service.get_token_info(token.address)


@router.post("/add_token/{address}", response_model=TokenInfo)
async def add_token(
    address: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
) -> TokenInfo:
    token_service = TokenService(db)
    try:
        token = token_service.add_new_token(address, background_tasks)
        # Schedule the collect_token_info to run in the background
        return token
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/get_holders_info/{address}", response_model=List[HolderModel])
async def get_holders_info(address: str, db: Session = Depends(get_db)) -> List[HolderModel]:
    # Запрос к базе данных для получения информации о холдерах
    token = db.query(Token).filter(Token.address == address).first()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Token with address {address} not found."
        )
    holder_service = HolderService(db)
    return holder_service.update_holders_info(token.address)
