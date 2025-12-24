from fastapi import FastAPI, Depends, HTTPException, status  # Import FastAPI class and Depends function from fastapi module
from sqlalchemy.orm import Session # Import Session class from sqlalchemy.orm module
from app.database import engine , get_db # Import the database engine and get_db function
from app.models import Task, Organization, User # Import the models
from pydantic import BaseModel # Import BaseModel for request validation
from app.security import hash_password, verify_password # Import security functions
from app.auth import create_access_token, get_current_user # Import function to create access tokens
from app.authorization import require_admin # Import admin authorization function

# Pydantic models for request validation
class OrganizationCreate(BaseModel):
    name: str

class TaskCreate(BaseModel):
    title: str
    status: str
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
    task_data: dict, 
    current_user: dict = Depends(get_current_user), 
    db: Session = Depends(get_db)):
    require_admin(current_user)

    task = Task(
        title=task_data["title"],
        status=task_data["status"],
        organization_id=current_user["organization_id"]
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    task = Task(
        title=task_data["title"],
        status=task_data["status"],
        organization_id=current_user["organization_id"]
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task 


@app.post("/signup")
def signup_user(
    email: str,
    password: str,
    organization_id: int,
    role: str = "USER",
    db: Session = Depends(get_db)
):
    # Check if organization exists
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(status_code=400, detail="Organization not found")
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pwd = hash_password(password)

    user = User(
        email=email,
        hashed_password=hashed_pwd,
        role=role,
        organization_id=organization_id
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "organization_id": user.organization_id
    }


@app.post("/login") # User login endpoint
def login_user(
    credentials: dict, 
    db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials["email"]).first()

    if not user:
        return {"error": "Invalid credentials"}

    if not verify_password(credentials["password"], user.hashed_password):
        return {"error": "Invalid credentials"}

    token = create_access_token({
        "user_id": user.id,
        "organization_id": user.organization_id,
        "role": user.role
    })

    return {"access_token": token}

@app.put("/tasks/{task_id}") # Update task endpoint
def update_task(
    task_id: int, 
    task_data: dict, 
    current_user: dict =Depends(get_current_user), 
    db: Session=Depends(get_db)): # Update a task by ID
    task=db.query(Task).filter(Task.id==task_id, Task.organization_id==current_user["organization_id"]).first() # Query the database for the task with the given ID and organization ID
    
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    if current_user["role"]=="USER":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Users cannot update tasks") # Only admins can update tasks
    
    task.title=task_data["title"] # Update the task's title
    task.status=task_data["status"] # Update the task's status

    db.commit()
    db.refresh(task)
    return task

# Enforces ownership and role-based authorization for task updates
# Prevents cross-tenant access
# DB and BE both enforce these rules

