from datetime import datetime, timedelta # Import datetime and timedelta for handling time-related tasks
from jose import jwt # Import jwt module from jose for handling JSON Web Tokens

SECRET_KEY= "cHANGE_LATER" # Secret key for encoding and decoding JWTs
ALGORITHM= "HS256" # Algorithm used for JWT encoding and decoding
ACCESS_TOKEN_EXPIRE_MINUTES=30 # Token expiration time in minutes

def create_access_token(data: dict):
    to_encode=data.copy() # Create a copy of the data to encode
    expire=datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # Calculate expiration time
    to_encode.update({"exp": expire}) # Add expiration time to the data
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # Encode and return the JWT   