# creates a metadata registry to track all the models
# without Base no tables can be created in the database
from sqlalchemy.orm import DeclarativeBase # Base class for declarative models
from sqlalchemy import Integer,String,ForeignKey,DateTime # Data types for model attributes
from sqlalchemy.orm import Mapped, mapped_column # For defining mapped columns
from datetime import datetime # For handling date and time  
class Base(DeclarativeBase):
    
    
# Organization model representing organizations in the database
class Organization(Base):
    __tablename__="organizations" # Tells SQLalchemy to create a Table called organizations in the database
    id:Mapped[int]=mapped_column(Integer, primary_key=True) # Primary key column
    # PK: unique row identification, Fastlookup, not null, required for relationships
    name:Mapped[str]=mapped_column(String, nullable=False) # Name column

# User model representing users in the database
class User(Base):
    __tablename__="users" # Tells SQLalchemy to create a Table called users in the database
    id: Mapped[int]=mapped_column(Integer, primary_key=True) # Primary key column
    email: Mapped[str]=mapped_column(String, unique=True, nullable=False) # Email column
    hashed_password: Mapped[str]=mapped_column(String, nullable=False) # Hashed password column
    role: Mapped[str]=mapped_column(String, nullable=False) # Role column

    organization_id: Mapped[int]=mapped_column(
        ForeignKey("organizations.id"), nullable=False
    ) # Foreign key column referencing organizations table
    # FK: establishes relationship between two tables, ensures referential integrity

#task model representing tasks in the database
class Task(Base):  # Task model representing tasks in the database
    __tablename__="tasks" # Tells SQLAlchemy to create a Table called tasks in the database
    id: Mapped[int]=mapped_column(Integer, primary_key=True) # Primary key column
    title: Mapped[str]=mapped_column(String, nullable=False) # Title column
    status: Mapped[str]=mapped_column(String, nullable=False) # Status column
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow) # Created at column with default value

    organization_id: Mapped[int]=mapped_column(ForeignKey("organizations.id"), nullable=False) # Foreign key column referencing organizations table