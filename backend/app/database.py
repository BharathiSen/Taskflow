from sqlalchemy import text # For executing raw SQL queries
from sqlalchemy import create_engine # Creates connection to the database
from sqlalchemy.orm import sessionmaker # Manages database sessions

DATABASE_URL = "postgresql://postgres:bharathi@localhost:5432/taskflow_db" # Database connection URL

engine = create_engine(DATABASE_URL) # Create the database engine
SessionLocal = sessionmaker(bind=engine) # One Database session per request 

def test_connection(): 

    db=SessionLocal() # Create a new database session
    try:
        db.execute(text("SELECT 1")) # Simple query to test connection
        print("Database connection successful")
    finally:
        db.close()