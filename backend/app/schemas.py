from pydantic import BaseModel # Import BaseModel for request validation
from typing import Literal  # Import Literal for defining specific allowed string values

class TaskCreate(BaseModel):  
    title: str
    status: Literal["CREATED"]

class TaskUpdate(BaseModel):
    status: Literal["IN_PROGRESS", "COMPLETED"]
