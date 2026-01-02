# TaskFlow — Multi-Tenant Task Management Backend

## 📋 Overview
TaskFlow is a production-ready backend service that enables multiple organizations to manage tasks securely with robust authentication, role-based authorization, and strict tenant isolation. Built with FastAPI and PostgreSQL, it demonstrates enterprise-grade backend architecture patterns.

## ✨ Features
- **JWT-based Authentication** — Secure token-based user authentication with expiration
- **Role-Based Access Control (RBAC)** — ADMIN and USER roles with permission enforcement
- **Multi-Tenant Data Isolation** — Organization-level data segregation at query level
- **Business Rule Validation** — Status transition rules (CREATED → IN_PROGRESS → COMPLETED)
- **RESTful CRUD APIs** — Full task lifecycle management
- **Pagination & Filtering** — Efficient data retrieval with DB-level pagination
- **In-Memory Caching** — 60-second TTL cache with smart invalidation
- **Centralized Error Handling** — HTTP status codes (400, 401, 403, 404, 500)
- **Structured Logging** — Request tracking and error monitoring
- **Environment-Based Configuration** — Secure secrets management

## 🛠️ Tech Stack
- **Framework**: FastAPI (async Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT (python-jose[cryptography])
- **Password Hashing**: bcrypt via passlib
- **Caching**: In-memory (Redis-ready architecture)
- **Server**: Uvicorn (ASGI server)

## 🚀 Setup

### Prerequisites
- Python 3.10+
- PostgreSQL 12+

### Installation
```bash
# Clone repository
git clone https://github.com/BharathiSen/Taskflow.git
cd Taskflow/backend

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Create .env file (see Environment Variables section)

# Run server
uvicorn app.main:app --reload
```

Server runs at: `http://localhost:8000`  
API docs: `http://localhost:8000/docs`

## 🔐 Environment Variables
Create a `.env` file in the `backend/` directory:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://username:password@localhost:5432/taskflow_db
```

**Security Note**: Never commit `.env` to version control. Generate a strong SECRET_KEY for production:
```python
import secrets
print(secrets.token_urlsafe(32))
```

## 🏗️ Architecture

### Request Flow
```
Client → JWT Token → FastAPI → Cache Layer → Database → Response
                        ↓
                   Authorization Check
                        ↓
                  Tenant Isolation Filter
```

### Multi-Tenancy Strategy
**Problem**: Multiple organizations sharing one backend must not access each other's data.

**Solution**: 
1. Every user belongs to an `organization_id` (stored in JWT)
2. All queries enforce: `WHERE organization_id = current_user.organization_id`
3. Cache keys include `org_id` for isolation
4. Foreign keys enforce referential integrity

**Example Query**:
```python
db.query(Task).filter(
    Task.organization_id == current_user["organization_id"]
).all()
```

### Database Schema
```
Organizations (id, name)
    ↓ (1:N)
Users (id, email, hashed_password, role, organization_id)
    ↓ (1:N)
Tasks (id, title, status, created_at, organization_id)
```

## 📡 API Endpoints

### Authentication
- `POST /signup` — Create new user
- `POST /login` — Get JWT token

### Organizations
- `POST /organizations` — Create organization

### Tasks (Protected)
- `GET /tasks` — List tasks (paginated, filterable, cached)
- `POST /tasks` — Create task (ADMIN only)
- `PUT /tasks/{id}` — Update task status (ADMIN only)
- `DELETE /tasks/{id}` — Delete task (ADMIN only)

### System
- `GET /health` — Health check

## 🔒 Security Features

### Authentication & Authorization
- Passwords hashed with bcrypt (cost factor 12)
- JWT tokens expire after 30 minutes
- Role-based access control on sensitive endpoints
- ADMIN role required for task mutations

### Data Isolation
- Organization-scoped queries prevent cross-tenant access
- JWT includes `organization_id` for runtime enforcement
- Cache invalidation is tenant-aware

### Error Handling
- Generic 500 errors prevent information leakage
- Full stack traces logged server-side only
- Consistent JSON error responses

## ⚡ Caching Strategy

### What's Cached
- `GET /tasks` endpoint (read-heavy operation)

### Cache Keys
```
tasks:{org_id}:{status}:{page}:{limit}
```

### Invalidation
Cache is cleared for an organization when:
- Task is created
- Task is updated
- Task is deleted

### Interview Answer
> "I cache frequently-read endpoints like task lists with a 60-second TTL. Cache keys include organization_id to maintain tenant isolation. Any write operation (create/update/delete) triggers explicit cache invalidation for that tenant, ensuring data consistency."

## 🧪 Testing the API

### 1. Create Organization
```bash
curl -X POST http://localhost:8000/organizations \
  -H "Content-Type: application/json" \
  -d '{"name": "Acme Corp"}'
```

### 2. Signup User
```bash
curl -X POST http://localhost:8000/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@acme.com",
    "password": "secure123",
    "organization_id": 1,
    "role": "ADMIN"
  }'
```

### 3. Login
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@acme.com",
    "password": "secure123"
  }'
```

### 4. Create Task (use token from login)
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Launch product",
    "status": "CREATED"
  }'
```

## 📚 Key Learning Outcomes

### Backend Fundamentals
- Request/response lifecycle in REST APIs
- Database design with proper relationships (1:N)
- ORM usage (SQLAlchemy) vs raw SQL

### Authentication & Authorization
- Difference between authentication ("who?") and authorization ("what can you do?")
- Why JWTs are stateless and scalable
- Password hashing vs encryption

### Multi-Tenancy
- Query-level tenant isolation
- Preventing data leakage across organizations
- Tenant-aware caching

### Production Patterns
- Environment-based configuration
- Centralized error handling
- Structured logging
- Pagination at database level
- Cache invalidation strategies

## 🎯 Interview Talking Points

### "Walk me through your authentication flow"
> "User submits credentials to /login. I verify the hashed password, then generate a JWT containing user_id, organization_id, and role. The token expires in 30 minutes. On subsequent requests, the token is decoded to identify the user and enforce authorization."

### "How do you prevent one organization from seeing another's data?"
> "Every user has an organization_id in their JWT. All database queries include a filter: WHERE organization_id = current_user.organization_id. This is enforced at the query level, not application logic, preventing data leakage even if authorization checks fail."

### "Why paginate at the database level?"
> "Fetching all records and paginating in-memory is inefficient. Using LIMIT/OFFSET at the DB level means only the required rows are retrieved, reducing memory usage and network transfer."

### "When does your cache become stale?"
> "Cache has a 60-second TTL, but I also invalidate explicitly on writes. When a task is created, updated, or deleted, I clear all cache entries for that organization. This ensures data consistency while maintaining read performance."

## 🚧 Future Enhancements
- [ ] Redis for distributed caching
- [ ] Async database operations
- [ ] Rate limiting per organization
- [ ] Audit logs for compliance
- [ ] Task assignments to specific users
- [ ] WebSocket notifications for real-time updates
- [ ] Unit and integration tests
- [ ] Docker containerization
- [ ] CI/CD pipeline

## 📄 License
MIT

## 👤 Author
**Bharathi Sen**  
GitHub: [@BharathiSen](https://github.com/BharathiSen)