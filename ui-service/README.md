# Sample API UI Service

React-based UI for managing Products and Orders through the microservices APIs.

## Setup

```bash
# Install dependencies
npm install

# Start the development server (runs on port 3000)
npm start
```

## Features

- **Login**: Authenticate with username/password (JWT-based)
- **Product Management**: View, create, edit, and delete products
- **Order Management**: View, create, cancel, and delete orders

## API Connections

This UI directly connects to:
- Login Service: http://localhost:8001
- Product Service: http://localhost:8002
- Order Service: http://localhost:8003

## Demo Credentials

- admin / admin123
- user1 / password123
- user2 / password456
