from fastapi import HTTPException, status  # Import HTTPException and status from fastapi module

def require_admin(current_user: dict):
    if current_user["role"]!="ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )