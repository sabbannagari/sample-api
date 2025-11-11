# Sample API Microservices

A complete microservices architecture with JWT authentication and React UI.

## Architecture

This project consists of 4 independent services:

1. **Login Service** (Port 8001) - JWT-based authentication
2. **Product Service** (Port 8002) - Product inventory management
3. **Order Service** (Port 8003) - Order processing
4. **UI Service** (Port 3000) - React frontend

## Features

- **JWT Authentication**: Secure token-based auth with bcrypt password hashing
- **Microservices**: Independent services with their own APIs
- **React UI**: Modern web interface for managing products and orders
- **RESTful APIs**: Complete CRUD operations for all resources

## Quick Start

### 1. Setup (First Time Only)

```bash
# Install Python dependencies
./setup.sh

# The .env file is already created with a default JWT_SECRET_KEY
# For production, generate a new secret key:
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Then update JWT_SECRET_KEY in .env file
```

### 2. Start Services

```bash
# Start all services (backend + UI)
./start.sh

# Or start individual services
./start.sh login      # Login service only
./start.sh product    # Product service only
./start.sh order      # Order service only
./start.sh ui         # UI service only
```

### 3. Access the Application

- **UI**: http://localhost:3000
- **Login API**: http://localhost:8001/docs
- **Product API**: http://localhost:8002/docs
- **Order API**: http://localhost:8003/docs

### 4. Stop Services

```bash
# Stop all services
./stop.sh

# Or stop individual services
./stop.sh login
./stop.sh ui
```

## Demo Credentials

- **admin** / admin123 (Admin role)
- **user1** / password123 (User role)
- **user2** / password456 (User role)

## Service Details

### Login Service (Port 8001)

**Endpoints:**
- `POST /login/credentials` - Login with username/password
- `POST /login/token` - Validate existing token
- `GET /me` - Get current user info
- `POST /logout` - Logout
- `GET /validate` - Validate token

**Technology:**
- FastAPI
- JWT tokens (PyJWT)
- Bcrypt password hashing

### Product Service (Port 8002)

**Endpoints:**
- `GET /products` - List all products (with filters)
- `GET /products/{id}` - Get product by ID
- `GET /products/sku/{sku}` - Get product by SKU
- `POST /products` - Create product
- `PUT /products/{id}` - Update product
- `DELETE /products/{id}` - Delete product
- `PATCH /products/{id}/stock` - Update stock
- `GET /categories` - Get all categories

**Authentication:** All endpoints require JWT token

### Order Service (Port 8003)

**Endpoints:**
- `GET /orders` - List all orders (with filters)
- `GET /orders/{id}` - Get order by ID
- `POST /orders` - Create order
- `PUT /orders/{id}` - Update order
- `DELETE /orders/{id}` - Delete order
- `POST /orders/{id}/cancel` - Cancel order
- `GET /users/{user_id}/orders/summary` - Get user order summary

**Authentication:** All endpoints require JWT token

### UI Service (Port 3000)

**Features:**
- Login page with authentication
- Product management (CRUD operations)
- Order management (Create, view, cancel, delete)
- Responsive design
- Direct API communication (no proxy)

**Technology:**
- React 18
- React Router
- Axios
- CSS3

## How Authentication Works

1. User logs in via `/login/credentials` with username + password
2. Login service validates credentials and returns JWT token
3. UI stores token in localStorage
4. All subsequent requests to Product/Order services include token in header: `Authorization: Bearer <token>`
5. Product/Order services validate JWT token **locally** (no network call to login service)
6. JWT tokens expire after 60 minutes

## Project Structure

```
sample-api/
├── login/                  # Login service
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── product-service/        # Product service
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── order-service/          # Order service
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── ui-service/             # React UI
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── App.js
│   └── package.json
├── jwt_config.py           # Shared JWT configuration
├── requirements.txt        # Python dependencies
├── setup.sh               # Setup script
├── start.sh               # Start services
└── stop.sh                # Stop services
```

## Development

### Adding New Endpoints

Each service is independent. To add new endpoints:

1. Edit the service's `main.py`
2. Add models to `models.py`
3. Add schemas to `schemas.py`
4. Restart the service: `./stop.sh <service> && ./start.sh <service>`

### Modifying UI

```bash
cd ui-service
npm start  # Development mode with hot reload
```

## Environment Configuration

### JWT Secret Key

All services share the same JWT secret key via the `.env` file:

```bash
# .env
JWT_SECRET_KEY=your-secret-key-here
```

**Important:**
- All services (login, product, order) load the key from `.env`
- The key is used to sign and verify JWT tokens
- Change the default key before deploying to production
- Never commit `.env` to version control (already in `.gitignore`)

**Generate a strong key:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Security Notes

⚠️ **This is a demo project. For production use:**

- ✅ Change `JWT_SECRET_KEY` in `.env` file (use a strong random string)
- Enable HTTPS
- Add rate limiting
- Implement refresh tokens
- Add CORS configuration
- Use a proper database instead of in-memory storage
- Add input validation and sanitization
- Implement proper logging and monitoring
- Store `.env` securely (use secrets management in cloud)

## License

MIT
