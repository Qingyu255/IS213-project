from typing import TypeVar, Type, Optional, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from sqlalchemy.orm import DeclarativeMeta

T = TypeVar('T', bound=DeclarativeMeta)

class BaseService:
    def __init__(self, model: Type[T]):
        self.model = model

    async def get_by_id(self, db: AsyncSession, id_value: Any, id_field: str) -> Optional[T]:
        result = await db.execute(
            select(self.model).filter(getattr(self.model, id_field) == id_value)
        )
        return result.scalars().first()

    async def create(self, db: AsyncSession, data: Dict[str, Any]) -> T:
        db_obj = self.model(**data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, db_obj: T, data: Dict[str, Any]) -> T:
        for field, value in data.items():
            setattr(db_obj, field, value)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    def raise_not_found(self, detail: str = "Item not found"):
        raise HTTPException(status_code=404, detail=detail)

    def raise_validation_error(self, detail: str):
        raise HTTPException(status_code=400, detail=detail) 