from typing import Annotated

from fastapi import Depends
from app.db.crud import TradingRepository
from app.db.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_trading_repository(session: SessionDep) -> TradingRepository:
    return TradingRepository(session)


TradingRepositoryDep = Annotated[TradingRepository, Depends(get_trading_repository)]
