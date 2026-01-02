from sqlalchemy import text # For executing raw SQL queries
from sqlalchemy import create_engine # Creates connection to the database
from sqlalchemy.orm import sessionmaker # Manages database sessions
from app.models import Base  # Importing the Base class from models
from app.config import DATABASE_URL # Import DATABASE_URL from config

engine = create_engine(DATABASE_URL) # Create the database engine
SessionLocal = sessionmaker(bind=engine) # One Database session per request 

Base.metadata.create_all(bind=engine) # Create all tables in the database based on the models

def get_db(): 
    """Dependency that provides a database session."""
    db = SessionLocal() # Create a new database session
    try:
        yield db # Yield the session to be used in the request
    finally:
        db.close() # Ensure the session is closed after the request