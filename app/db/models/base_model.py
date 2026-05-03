from datetime import datetime
from typing import Annotated
from uuid import UUID
from sqlalchemy import UUID as sqlalchemy_UUID

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.ext.asyncio import AsyncAttrs

from sqlalchemy import TIMESTAMP, func

from sqlalchemy.orm import mapped_column

created_time = Annotated[datetime, mapped_column(TIMESTAMP(timezone=True), server_default=func.now())]
updated_time = Annotated[
    datetime, mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    metadata = MetaData()

    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        """Relationships не используются в repr(), т.к. могут вести к неожиданным подгрузкам"""
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"

    created_at: Mapped[created_time]
    updated_at: Mapped[updated_time]
