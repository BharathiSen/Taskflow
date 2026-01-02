from datetime import datetime, timedelta # Import datetime and timedelta for handling time-related tasks
from jose import JWTError, jwt # Import JWTError and jwt module from jose for handling JSON Web Tokens
from fastapi import Depends, HTTPException, status # Import Depends function from FastAPI for dependency injection
from fastapi.security import OAuth2PasswordBearer # Import OAuth2PasswordBearer for handling OAuth2 authentication
from app.config import SECRET_KEY # Import SECRET_KEY from config

ALGORITHM= "HS256" # Algorithm used for JWT encoding and decoding
ACCESS_TOKEN_EXPIRE_MINUTES=30 # Token expiration time in minutes

def create_access_token(data: dict):
    to_encode=data.copy() # Create a copy of the data to encode
    expire=datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # Calculate expiration time
    to_encode.update({"exp": expire}) # Add expiration time to the data
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # Encode and return the JWT   

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # OAuth2 scheme for token URL
def get_current_user(token: str = Depends(oauth2_scheme)): # Dependency to get the current user from the token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # Decode the JWT to get the payload
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )