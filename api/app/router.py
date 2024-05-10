import logging
from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.holder import HolderModel
from app.services.holder_service import HolderService
from app.repository.token_repository import get_token_repository
from app.services.token_service import TokenService
from app import get_db
from app.models.token import Token, TokenData, TokenModel

router = APIRouter()
logger = logging.getLogger("resources")


@router.get("/get_token_info/{address}", response_model=TokenData)
async def get_token_info(address: str, db: Session = Depends(get_db)) -> TokenData:
    """
    Retrieve detailed information about a token.

    Args:
        address (str): The address of the token.

    Returns:
        TokenData: Detailed information about the token.

    Raises:
        HTTPException: If the token with the specified address is not found.

    Notes:
        This endpoint uses the `TokenService` and `get_token_repository` to retrieve token information.
    """
    token_service = TokenService(db)
    token_rep = get_token_repository(db)
    token = token_rep.get_or_404(address)
    return token_service.get_token_info(token.address)


@router.post("/add_token/{address}", response_model=TokenModel)
async def add_token(
    address: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
) -> TokenModel:
    """
    Add a new token to the database.

    Args:
        address (str): The address of the token.
        background_tasks (BackgroundTasks): Background tasks to execute asynchronously.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        TokenModel: The added token model.

    Raises:
        HTTPException: If an error occurs while adding the token.

    Notes:
        This endpoint uses the `TokenService` to add the token asynchronously with background tasks.
    """
    token_service = TokenService(db)
    try:
        token = token_service.add_new_token(address, background_tasks)
        return token
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/get_holders_info/{address}", response_model=List[HolderModel])
async def get_holders_info(address: str, db: Session = Depends(get_db)) -> List[HolderModel]:
    """
    Retrieve information about token holders.

    Args:
        address (str): The address of the token.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        List[HolderModel]: Information about token holders.

    Raises:
        HTTPException: If the token with the specified address is not found.

    Notes:
        This endpoint uses the `HolderService` to retrieve and update information about token holders.
    """
    token = db.query(Token).filter(Token.address == address).first()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Token with address {address} not found."
        )
    holder_service = HolderService(db)
    return holder_service.update_holders_info(token.address)
