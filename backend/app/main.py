from fastapi import FastAPI, Depends, HTTPException, status, Request  # Import FastAPI class and Depends function from fastapi module
from sqlalchemy.orm import Session # Import Session class from sqlalchemy.orm module
from app.database import engine , get_db # Import the database engine and get_db function
from app.models import Task, Organization, User # Import the models
from pydantic import BaseModel # Import BaseModel for request validation
from app.security import hash_password, verify_password # Import security functions
from app.auth import create_access_token, get_current_user # Import function to create access tokens
from app.authorization import require_admin # Import admin authorization function
from app.rules import validate_status_transition # Import status transition validation function
from app.schemas import TaskCreate, TaskUpdate # Import task schemas
from app.exceptions import BusinessRuleViolation # Import custom exception
from fastapi.responses import JSONResponse # Import JSONResponse for custom error handling


# Pydantic models for request validation
class OrganizationCreate(BaseModel):
    name: str

class SignupRequest(BaseModel):
    email: str
    password: str
    organization_id: int
    role: str = "USER"

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    organization_id: int

app = FastAPI() # Create an instance of FastAPI

@app.get("/") # Define a GET endpoint at root
def root():
    return {
        "message": "Taskflow API", 
        "endpoints": {
            "health": "/health",
            "tasks": "/tasks",
            "docs": "/docs"
        }
    }

@app.get("/health") # Define a GET endpoint at /health
def health(): # Define the health function
    return {"status": "OK"} # Return a JSON response indicating the service is healthy

@app.post("/organizations") # Create organization endpoint
def create_organization(
    org_data: OrganizationCreate, 
    db: Session = Depends(get_db)):

    org = Organization(**org_data.model_dump())
    db.add(org)
    db.commit()
    db.refresh(org)
    return org

@app.get("/tasks") # Registers a GET endpoint at /tasks
def get_tasks( 
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)):
    return db.query(Task).filter(
        Task.organization_id == current_user["organization_id"]
    ).all()


@app.post("/tasks")
def create_task(
    data: TaskCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_admin(current_user)

    task = Task(
        title=data.title,
        status=data.status,
        organization_id=current_user["organization_id"]
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task 


@app.post("/signup", response_model=UserResponse)
def signup_user(
    signup_data: SignupRequest,
    db: Session = Depends(get_db)
):
    # Check if organization exists
    org = db.query(Organization).filter(Organization.id == signup_data.organization_id).first()
    if not org:
        raise HTTPException(status_code=400, detail="Organization not found")
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == signup_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pwd = hash_password(signup_data.password)

    user = User(
        email=signup_data.email,
        hashed_password=hashed_pwd,
        role=signup_data.role,
        organization_id=signup_data.organization_id
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@app.post("/login", response_model=TokenResponse) # User login endpoint
def login_user(
    credentials: LoginRequest, 
    db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token({
        "user_id": user.id,
        "organization_id": user.organization_id,
        "role": user.role
    })

    return {"access_token": token}

@app.put("/tasks/{task_id}") # Update task endpoint
def update_task(
    task_id: int,
    new_status: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_admin(current_user)

    task = db.query(Task).filter(
        Task.id == task_id,
        Task.organization_id == current_user["organization_id"]
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        validate_status_transition(task.status, new_status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    task.status = new_status
    db.commit()
    db.refresh(task)

    return task

@app.delete("/tasks/{task_id}") # Delete task endpoint
def delete_task(
    task_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_admin(current_user)

    task = db.query(Task).filter(
        Task.id == task_id,
        Task.organization_id == current_user["organization_id"]
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()

    return {"message": "Task deleted successfully"}

# Enforces ownership and role-based authorization for task updates
# Prevents cross-tenant access
# DB and BE both enforce these rules

@app.get("/tasks")
def get_tasks(
    status: str | None = None,
    page: int = 1,
    limit: int = 10,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if page < 1: 
        raise HTTPException(status_code=400, detail="Page must be >= 1")
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")

    query = db.query(Task).filter(
        Task.organization_id == current_user["organization_id"]
    )

    if status:
        query = query.filter(Task.status == status)

    offset = (page - 1) * limit

    return query.offset(offset).limit(limit).all()

@app.exception_handler(BusinessRuleViolation)
def business_rule_exception_handler(
    request: Request,
    exc: BusinessRuleViolation
):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message}
    )
