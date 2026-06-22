import os
import uuid
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from database.models import User, Session, UploadedFile, DocumentChunk, Message, SessionLocal

def seed_database():
    session = SessionLocal()
    try:
        # Insert sample users
        user1 = User(id=uuid.uuid4(), session_id="session_001", created_at=datetime.utcnow())
        user2 = User(id=uuid.uuid4(), session_id="session_002", created_at=datetime.utcnow())
        user3 = User(id=uuid.uuid4(), session_id="session_003", created_at=datetime.utcnow())
        session.add_all([user1, user2, user3])
        session.commit()

        # Insert sample sessions
        session1 = Session(id=uuid.uuid4(), user_id=user1.id, name="Session One", created_at=datetime.utcnow())
        session2 = Session(id=uuid.uuid4(), user_id=user2.id, name="Session Two", created_at=datetime.utcnow())
        session3 = Session(id=uuid.uuid4(), user_id=user3.id, name="Session Three", created_at=datetime.utcnow())
        session.add_all([session1, session2, session3])
        session.commit()

        # Insert sample uploaded files
        file1 = UploadedFile(
            id=uuid.uuid4(),
            session_id=session1.id,
            filename="file1.xlsx",
            file_path="/uploads/file1.xlsx",
            file_size=1024,
            uploaded_at=datetime.utcnow()
        )
        file2 = UploadedFile(
            id=uuid.uuid4(),
            session_id=session2.id,
            filename="file2.xlsx",
            file_path="/uploads/file2.xlsx",
            file_size=2048,
            uploaded_at=datetime.utcnow()
        )
        file3 = UploadedFile(
            id=uuid.uuid4(),
            session_id=session3.id,
            filename="file3.xlsx",
            file_path="/uploads/file3.xlsx",
            file_size=4096,
            uploaded_at=datetime.utcnow()
        )
        session.add_all([file1, file2, file3])
        session.commit()

        # Insert sample document chunks
        chunk1 = DocumentChunk(
            id=uuid.uuid4(),
            uploaded_file_id=file1.id,
            content="Chunk 1 content",
            chunk_index=0,
            start_row=1,
            end_row=10,
            sheet_name="Sheet1",
            embedding=[0.1] * 1536,
            created_at=datetime.utcnow()
        )
        chunk2 = DocumentChunk(
            id=uuid.uuid4(),
            uploaded_file_id=file2.id,
            content="Chunk 2 content",
            chunk_index=1,
            start_row=11,
            end_row=20,
            sheet_name="Sheet2",
            embedding=[0.2] * 1536,
            created_at=datetime.utcnow()
        )
        chunk3 = DocumentChunk(
            id=uuid.uuid4(),
            uploaded_file_id=file3.id,
            content="Chunk 3 content",
            chunk_index=2,
            start_row=21,
            end_row=30,
            sheet_name="Sheet3",
            embedding=[0.3] * 1536,
            created_at=datetime.utcnow()
        )
        session.add_all([chunk1, chunk2, chunk3])
        session.commit()

        # Insert sample messages
        message1 = Message(
            id=uuid.uuid4(),
            session_id=session1.id,
            role="user",
            content="Hello, assistant!",
            citations=None,
            created_at=datetime.utcnow()
        )
        message2 = Message(
            id=uuid.uuid4(),
            session_id=session2.id,
            role="assistant",
            content="How can I help you today?",
            citations=None,
            created_at=datetime.utcnow()
        )
        message3 = Message(
            id=uuid.uuid4(),
            session_id=session3.id,
            role="system",
            content="Session initialized.",
            citations=None,
            created_at=datetime.utcnow()
        )
        session.add_all([message1, message2, message3])
        session.commit()

        print("Database seeded successfully!")

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error seeding database: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed_database()