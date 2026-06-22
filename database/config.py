import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.exc import OperationalError

# Read DATABASE_URL from environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set.")

# SQLAlchemy engine configuration
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

# SessionLocal factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base class for models
class Base(DeclarativeBase):
    pass

# Dependency for FastAPI to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to initialize the database (create all tables)
def init_db():
    from database.models import Base  # Ensure all models are imported
    Base.metadata.create_all(bind=engine)

# Health check function to test the database connection
def check_db_health():
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True
    except OperationalError:
        return False