from passlib.context import CryptoContext 
pwd_context = CryptoContext(schemes=["bcrypt"], deprecated="auto") # Password hashing context using bcrypt algorithm

def hash_password(password: str) -> str: # Function to hash a plain password
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool: # Function to verify a plain password against a hashed password
    return pwd_context.verify(plain_password, hashed_password)
