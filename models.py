# Simulated DB
users_db = [
    {"id": 1, "name": "John Doe", "email": "john@example.com"},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
]

# Tasks/Todos DB
tasks_db = [
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
]

