from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from models import users_db, tasks_db
from schemas import User, UserCreate, UserUpdate, Task, TaskCreate, TaskUpdate
from typing import Optional
from datetime import datetime

app = FastAPI(
    title="User Management API",
    description="Sample API for demonstrating agentic API testing",
    version="1.0.0"
)

# Middleware to validate query parameters
@app.middleware("http")
async def validate_query_params(request: Request, call_next):
    if request.url.path == "/users" and request.method == "GET":
        allowed_params = {"limit", "offset"}
        query_params = set(request.query_params.keys())
        invalid_params = query_params - allowed_params
        if invalid_params:
            return JSONResponse(
                status_code=422,
                content={"detail": f"Invalid query parameter(s): {', '.join(invalid_params)}"}
            )
    response = await call_next(request)
    return response

# 1. List users
@app.get("/users", response_model=list[User])
def list_users(
    limit: Optional[int] = Query(None, ge=1, le=100, description="Limit number of results"),
    offset: Optional[int] = Query(None, ge=0, description="Offset for pagination")
):
    # Apply pagination if parameters are provided
    start = offset if offset is not None else 0
    end = start + limit if limit is not None else len(users_db)
    return users_db[start:end]

# 2. Get user by ID
@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    for user in users_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

# 3. Create user
@app.post("/users", response_model=User, status_code=201)
def create_user(new_user: UserCreate):
    # Check for duplicate email
    for user in users_db:
        if user["email"] == new_user.email:
            raise HTTPException(status_code=400, detail="Email already exists")

    next_id = max(u["id"] for u in users_db) + 1 if users_db else 1
    created_user = {"id": next_id, **new_user.dict()}
    users_db.append(created_user)
    return created_user

# 4. Update user
@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, update: UserUpdate):
    for user in users_db:
        if user["id"] == user_id:
            # Check for duplicate email if email is being updated
            if update.email and update.email != user["email"]:
                for other_user in users_db:
                    if other_user["id"] != user_id and other_user["email"] == update.email:
                        raise HTTPException(status_code=400, detail="Email already exists")

            if update.name:
                user["name"] = update.name
            if update.email:
                user["email"] = update.email
            return user
    raise HTTPException(status_code=404, detail="User not found")

# 5. Delete user
@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    for user in users_db:
        if user["id"] == user_id:
            users_db.remove(user)
            return
    raise HTTPException(status_code=404, detail="User not found")

# 6. Reset database (for testing purposes)
@app.post("/reset-db", status_code=200)
def reset_database():
    users_db.clear()
    users_db.extend([
        {"id": 1, "name": "John Doe", "email": "john@example.com"},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
    ])
    tasks_db.clear()
    tasks_db.extend([
        {
            "id": 1,
            "user_id": 1,
            "title": "Complete project documentation",
            "description": "Write comprehensive API documentation",
            "status": "pending",
            "created_at": "2025-01-15T10:00:00",
            "updated_at": "2025-01-15T10:00:00",
            "due_date": "2025-01-20T23:59:59"
        },
        {
            "id": 2,
            "user_id": 1,
            "title": "Review pull requests",
            "description": "Review and merge pending PRs",
            "status": "completed",
            "created_at": "2025-01-14T09:00:00",
            "updated_at": "2025-01-15T14:30:00",
            "due_date": None
        },
        {
            "id": 3,
            "user_id": 2,
            "title": "Prepare presentation",
            "description": "Create slides for team meeting",
            "status": "pending",
            "created_at": "2025-01-15T11:00:00",
            "updated_at": "2025-01-15T11:00:00",
            "due_date": "2025-01-18T15:00:00"
        }
    ])
    return {"message": "Database reset successfully"}

# ==================== TASK/TODO ENDPOINTS ====================

# 7. List all tasks for a specific user
@app.get("/users/{user_id}/tasks", response_model=list[Task])
def list_user_tasks(user_id: int):
    # Check if user exists
    user_exists = any(user["id"] == user_id for user in users_db)
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")

    # Return all tasks for this user
    user_tasks = [task for task in tasks_db if task["user_id"] == user_id]
    return user_tasks

# 8. Get a specific task for a user
@app.get("/users/{user_id}/tasks/{task_id}", response_model=Task)
def get_user_task(user_id: int, task_id: int):
    # Check if user exists
    user_exists = any(user["id"] == user_id for user in users_db)
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")

    # Find the task
    for task in tasks_db:
        if task["id"] == task_id and task["user_id"] == user_id:
            return task

    raise HTTPException(status_code=404, detail="Task not found")

# 9. Create a new task for a user
@app.post("/users/{user_id}/tasks", response_model=Task, status_code=201)
def create_task(user_id: int, new_task: TaskCreate):
    # Check if user exists
    user_exists = any(user["id"] == user_id for user in users_db)
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate status
    if new_task.status not in ["pending", "completed"]:
        raise HTTPException(status_code=400, detail="Status must be 'pending' or 'completed'")

    # Generate new task ID
    next_id = max(t["id"] for t in tasks_db) + 1 if tasks_db else 1

    # Create task
    now = datetime.now().isoformat()
    created_task = {
        "id": next_id,
        "user_id": user_id,
        "title": new_task.title,
        "description": new_task.description,
        "status": new_task.status,
        "created_at": now,
        "updated_at": now,
        "due_date": new_task.due_date.isoformat() if new_task.due_date else None
    }
    tasks_db.append(created_task)
    return created_task

# 10. Update a task
@app.put("/users/{user_id}/tasks/{task_id}", response_model=Task)
def update_task(user_id: int, task_id: int, update: TaskUpdate):
    # Check if user exists
    user_exists = any(user["id"] == user_id for user in users_db)
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate status if provided
    if update.status and update.status not in ["pending", "completed"]:
        raise HTTPException(status_code=400, detail="Status must be 'pending' or 'completed'")

    # Find and update the task
    for task in tasks_db:
        if task["id"] == task_id and task["user_id"] == user_id:
            if update.title is not None:
                task["title"] = update.title
            if update.description is not None:
                task["description"] = update.description
            if update.status is not None:
                task["status"] = update.status
            if update.due_date is not None:
                task["due_date"] = update.due_date.isoformat()

            task["updated_at"] = datetime.now().isoformat()
            return task

    raise HTTPException(status_code=404, detail="Task not found")

# 11. Delete a task
@app.delete("/users/{user_id}/tasks/{task_id}", status_code=204)
def delete_task(user_id: int, task_id: int):
    # Check if user exists
    user_exists = any(user["id"] == user_id for user in users_db)
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")

    # Find and delete the task
    for task in tasks_db:
        if task["id"] == task_id and task["user_id"] == user_id:
            tasks_db.remove(task)
            return

    raise HTTPException(status_code=404, detail="Task not found")

# 12. Get all tasks (admin view - optional)
@app.get("/tasks", response_model=list[Task])
def list_all_tasks(
    status: Optional[str] = Query(None, description="Filter by status (pending/completed)"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Limit number of results"),
    offset: Optional[int] = Query(None, ge=0, description="Offset for pagination")
):
    # Filter by status if provided
    filtered_tasks = tasks_db
    if status:
        if status not in ["pending", "completed"]:
            raise HTTPException(status_code=400, detail="Status must be 'pending' or 'completed'")
        filtered_tasks = [task for task in tasks_db if task["status"] == status]

    # Apply pagination
    start = offset if offset is not None else 0
    end = start + limit if limit is not None else len(filtered_tasks)
    return filtered_tasks[start:end]

