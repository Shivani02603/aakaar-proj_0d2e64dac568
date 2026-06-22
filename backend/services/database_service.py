from uuid import UUID
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from database.models import User, Session, UploadedFile, DocumentChunk, Message
from datetime import datetime


class DatabaseService:
    async def create_user(self, session: AsyncSession, user_id: UUID, session_id: str) -> User:
        try:
            new_user = User(id=user_id, session_id=session_id, created_at=datetime.utcnow())
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            return new_user
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User creation failed due to integrity error."
            )

    async def get_user_by_id(self, session: AsyncSession, user_id: UUID) -> User:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found."
            )
        return user

    async def list_all_users(self, session: AsyncSession) -> List[User]:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return users

    async def update_user(self, session: AsyncSession, user_id: UUID, session_id: Optional[str]) -> User:
        user = await self.get_user_by_id(session, user_id)
        if session_id:
            user.session_id = session_id
        user.updated_at = datetime.utcnow()
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def delete_user(self, session: AsyncSession, user_id: UUID) -> None:
        user = await self.get_user_by_id(session, user_id)
        await session.delete(user)
        await session.commit()

    async def create_session(self, session: AsyncSession, session_id: UUID, user_id: UUID, name: str) -> Session:
        try:
            new_session = Session(id=session_id, user_id=user_id, name=name, created_at=datetime.utcnow())
            session.add(new_session)
            await session.commit()
            await session.refresh(new_session)
            return new_session
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session creation failed due to integrity error."
            )

    async def get_session_by_id(self, session: AsyncSession, session_id: UUID) -> Session:
        result = await session.execute(select(Session).where(Session.id == session_id))
        session_obj = result.scalar_one_or_none()
        if not session_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID {session_id} not found."
            )
        return session_obj

    async def list_all_sessions(self, session: AsyncSession) -> List[Session]:
        result = await session.execute(select(Session))
        sessions = result.scalars().all()
        return sessions

    async def update_session(self, session: AsyncSession, session_id: UUID, name: Optional[str]) -> Session:
        session_obj = await self.get_session_by_id(session, session_id)
        if name:
            session_obj.name = name
        session_obj.updated_at = datetime.utcnow()
        session.add(session_obj)
        await session.commit()
        await session.refresh(session_obj)
        return session_obj

    async def delete_session(self, session: AsyncSession, session_id: UUID) -> None:
        session_obj = await self.get_session_by_id(session, session_id)
        await session.delete(session_obj)
        await session.commit()

    async def create_uploaded_file(
        self, session: AsyncSession, file_id: UUID, session_id: UUID, filename: str, file_path: str, file_size: int
    ) -> UploadedFile:
        try:
            new_file = UploadedFile(
                id=file_id,
                session_id=session_id,
                filename=filename,
                file_path=file_path,
                file_size=file_size,
                uploaded_at=datetime.utcnow()
            )
            session.add(new_file)
            await session.commit()
            await session.refresh(new_file)
            return new_file
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File upload failed due to integrity error."
            )

    async def get_file_by_id(self, session: AsyncSession, file_id: UUID) -> UploadedFile:
        result = await session.execute(select(UploadedFile).where(UploadedFile.id == file_id))
        file = result.scalar_one_or_none()
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File with ID {file_id} not found."
            )
        return file

    async def list_all_files(self, session: AsyncSession) -> List[UploadedFile]:
        result = await session.execute(select(UploadedFile))
        files = result.scalars().all()
        return files

    async def update_file(
        self, session: AsyncSession, file_id: UUID, filename: Optional[str], file_path: Optional[str], file_size: Optional[int]
    ) -> UploadedFile:
        file = await self.get_file_by_id(session, file_id)
        if filename:
            file.filename = filename
        if file_path:
            file.file_path = file_path
        if file_size:
            file.file_size = file_size
        file.updated_at = datetime.utcnow()
        session.add(file)
        await session.commit()
        await session.refresh(file)
        return file

    async def delete_file(self, session: AsyncSession, file_id: UUID) -> None:
        file = await self.get_file_by_id(session, file_id)
        await session.delete(file)
        await session.commit()