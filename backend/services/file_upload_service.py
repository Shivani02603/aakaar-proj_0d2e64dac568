from uuid import UUID
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from database.models import UploadedFile
from datetime import datetime

class FileUploadService:
    @staticmethod
    async def create_file(
        session_id: UUID,
        filename: str,
        file_path: str,
        file_size: int,
        uploaded_at: Optional[datetime] = None,
        db: AsyncSession = None
    ) -> UploadedFile:
        if uploaded_at is None:
            uploaded_at = datetime.utcnow()
        new_file = UploadedFile(
            session_id=session_id,
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            uploaded_at=uploaded_at
        )
        try:
            db.add(new_file)
            await db.commit()
            await db.refresh(new_file)
            return new_file
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error creating file. Please check the input data."
            )

    @staticmethod
    async def get_file_by_id(file_id: UUID, db: AsyncSession) -> UploadedFile:
        result = await db.execute(select(UploadedFile).where(UploadedFile.id == file_id))
        file = result.scalar_one_or_none()
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File with ID {file_id} not found."
            )
        return file

    @staticmethod
    async def list_all_files(db: AsyncSession) -> List[UploadedFile]:
        result = await db.execute(select(UploadedFile))
        files = result.scalars().all()
        return files

    @staticmethod
    async def update_file(
        file_id: UUID,
        filename: Optional[str] = None,
        file_path: Optional[str] = None,
        file_size: Optional[int] = None,
        uploaded_at: Optional[datetime] = None,
        db: AsyncSession = None
    ) -> UploadedFile:
        file = await FileUploadService.get_file_by_id(file_id, db)
        if filename:
            file.filename = filename
        if file_path:
            file.file_path = file_path
        if file_size:
            file.file_size = file_size
        if uploaded_at:
            file.uploaded_at = uploaded_at
        try:
            db.add(file)
            await db.commit()
            await db.refresh(file)
            return file
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error updating file. Please check the input data."
            )

    @staticmethod
    async def delete_file(file_id: UUID, db: AsyncSession) -> None:
        file = await FileUploadService.get_file_by_id(file_id, db)
        try:
            await db.delete(file)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error deleting file."
            )