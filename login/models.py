# Login service database with bcrypt hashed passwords
# Password hashes are for: admin123, password123, password456 respectively
users_auth_db = [
    {
        "id": 1,
        "username": "admin",
        "password": "$2b$12$lKIDuoT3XiGLW6zMUvgvE.LfVzrIeXHs2A0o2tefcyUTF9obtyegK",  # admin123
        "email": "admin@example.com",
        "role": "admin"
    },
    {
        "id": 2,
        "username": "user1",
        "password": "$2b$12$hToQLXo54xGfJOYd5EtRKOi8BT.sAXfg5UNmKyKGiwEmKqSIt47y6",  # password123
        "email": "user1@example.com",
        "role": "user"
    },
    {
        "id": 3,
        "username": "user2",
        "password": "$2b$12$CSCzGo8zJHO0lvJSIEqopeFuRvQVWAnIBZnPG4OigTqs8qVhFXc2u",  # password456
        "email": "user2@example.com",
        "role": "user"
    }
]

# Active tokens storage (in production, use Redis or database)
active_tokens = {}
