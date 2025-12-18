from sqlalchemy import create_engine # Creates connection to the database
from sqlalchemy.orm import sessionmaker # Manages database sessions

DATABASE_URL = "postgresql://postgres:bharathirsa@28@localhost/taskflow_db" # Database connection URL

engine = create_engine(DATABASE_URL) # Create the database engine
SessionLocal = sessionmaker(bind=engine) # One Database session per request 