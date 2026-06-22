from uuid import UUID
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from database.models import Session
from datetime import datetime


class DeploymentService:
    async def create_deployment(
        self, name: str, user_id: UUID, db: AsyncSession
    ) -> Session:
        try:
            new_session = Session(
                id=UUID(),
                user_id=user_id,
                name=name,
                created_at=datetime.utcnow(),
            )
            db.add(new_session)
            await db.commit()
            await db.refresh(new_session)
            return new_session
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create deployment due to integrity error.",
            )

    async def get_deployment_by_id(self, session_id: UUID, db: AsyncSession) -> Session:
        result = await db.execute(select(Session).where(Session.id == session_id))
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deployment with ID {session_id} not found.",
            )
        return session

    async def list_all_deployments(self, db: AsyncSession) -> List[Session]:
        result = await db.execute(select(Session))
        sessions = result.scalars().all()
        return sessions

    async def update_deployment(
        self, session_id: UUID, name: Optional[str], db: AsyncSession
    ) -> Session:
        result = await db.execute(select(Session).where(Session.id == session_id))
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deployment with ID {session_id} not found.",
            )
        if name:
            session.name = name
        session.updated_at = datetime.utcnow()
        try:
            await db.commit()
            await db.refresh(session)
            return session
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update deployment due to integrity error.",
            )

    async def delete_deployment(self, session_id: UUID, db: AsyncSession) -> None:
        result = await db.execute(select(Session).where(Session.id == session_id))
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deployment with ID {session_id} not found.",
            )
        try:
            await db.delete(session)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete deployment due to integrity error.",
            )