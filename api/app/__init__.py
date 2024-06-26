from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
from app.config import POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER

# SQLALCHEMY_DATABASE_URL is constructed from environment variables
SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:5432/{POSTGRES_DB}"

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("resources")

# Create SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a sessionmaker to manage sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative class definitions
Base = declarative_base()

# Create database tables based on declarative base
Base.metadata.create_all(engine)

# Constants for JWT token generation and verification
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"


def get_db():
    """
    Function to get a database session.

    Yields:
        Session: A SQLAlchemy database session.

    Notes:
        The session is closed automatically after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
