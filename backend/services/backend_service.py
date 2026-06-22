from uuid import UUID
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from database.models import User, Session
from datetime import datetime


class BackendService:
    async def create_user(self, session_id: str, db: AsyncSession) -> User:
        try:
            new_user = User(session_id=session_id, created_at=datetime.utcnow())
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            return new_user
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user due to integrity error."
            )

    async def get_user_by_id(self, user_id: UUID, db: AsyncSession) -> User:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found."
            )
        return user

    async def list_all_users(self, db: AsyncSession) -> List[User]:
        result = await db.execute(select(User))
        users = result.scalars().all()
        return users

    async def update_user(self, user_id: UUID, session_id: Optional[str], db: AsyncSession) -> User:
        user = await self.get_user_by_id(user_id, db)
        if session_id:
            user.session_id = session_id
        user.updated_at = datetime.utcnow()
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def delete_user(self, user_id: UUID, db: AsyncSession) -> None:
        user = await self.get_user_by_id(user_id, db)
        await db.delete(user)
        await db.commit()

    async def create_session(self, user_id: UUID, name: str, db: AsyncSession) -> Session:
        try:
            new_session = Session(user_id=user_id, name=name, created_at=datetime.utcnow())
            db.add(new_session)
            await db.commit()
            await db.refresh(new_session)
            return new_session
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create session due to integrity error."
            )

    async def get_session_by_id(self, session_id: UUID, db: AsyncSession) -> Session:
        result = await db.execute(select(Session).where(Session.id == session_id))
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID {session_id} not found."
            )
        return session

    async def list_all_sessions(self, db: AsyncSession) -> List[Session]:
        result = await db.execute(select(Session))
        sessions = result.scalars().all()
        return sessions

    async def update_session(self, session_id: UUID, name: Optional[str], db: AsyncSession) -> Session:
        session = await self.get_session_by_id(session_id, db)
        if name:
            session.name = name
        session.updated_at = datetime.utcnow()
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    async def delete_session(self, session_id: UUID, db: AsyncSession) -> None:
        session = await self.get_session_by_id(session_id, db)
        await db.delete(session)
        await db.commit()