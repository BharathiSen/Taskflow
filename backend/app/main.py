from fastapi import FastAPI # Import FastAPI class from fastapi module
from app.database import engine # Import the database engine

app = FastAPI() # Create an instance of FastAPI

@app.get("/health") # Define a GET endpoint at /health
def health(): # Define the health function
    return {"status": "OK"} # Return a JSON response indicating the service is healthy

