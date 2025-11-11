from fastapi import FastAPI, HTTPException, Query, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .models import orders_db
from .schemas import Order, OrderCreate, OrderUpdate
from typing import Optional
from datetime import datetime
import jwt
import sys
import os

# Add parent directory to path to import jwt_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from jwt_config import SECRET_KEY, ALGORITHM

app = FastAPI(
    title="Order Management API",
    description="Independent service for managing customer orders (Requires JWT Authentication)",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React UI
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()
VALID_STATUSES = ["pending", "processing", "shipped", "delivered", "cancelled"]

# Authentication dependency - validates JWT token locally
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify the JWT token locally without calling login service.
    Returns user info if valid, raises 401 if invalid.
    """
    token = credentials.credentials

    try:
        # Decode and validate JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "role": payload.get("role")
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# 1. List all orders
@app.get("/orders", response_model=list[Order])
def list_orders(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Limit number of results"),
    offset: Optional[int] = Query(None, ge=0, description="Offset for pagination"),
    current_user: dict = Depends(verify_token)
):
    """
    Get all orders with optional filtering. Requires JWT authentication.
    """
    filtered_orders = orders_db

    # Apply filters
    if user_id is not None:
        filtered_orders = [o for o in filtered_orders if o["user_id"] == user_id]

    if status:
        if status not in VALID_STATUSES:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}")
        filtered_orders = [o for o in filtered_orders if o["status"] == status]

    # Apply pagination
    start = offset if offset is not None else 0
    end = start + limit if limit is not None else len(filtered_orders)

    return filtered_orders[start:end]

# 2. Get order by ID
@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: int, current_user: dict = Depends(verify_token)):
    """
    Get a specific order by ID. Requires JWT authentication.
    """
    for order in orders_db:
        if order["id"] == order_id:
            return order
    raise HTTPException(status_code=404, detail="Order not found")

# 3. Create new order
@app.post("/orders", response_model=Order, status_code=201)
def create_order(new_order: OrderCreate, current_user: dict = Depends(verify_token)):
    """
    Create a new order. Requires JWT authentication.
    """
    if not new_order.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")

    # Calculate total amount
    total_amount = sum(item.quantity * item.price for item in new_order.items)

    # Generate new ID
    next_id = max(o["id"] for o in orders_db) + 1 if orders_db else 1

    now = datetime.now().isoformat()

    created_order = {
        "id": next_id,
        "user_id": new_order.user_id,
        "items": [item.dict() for item in new_order.items],
        "total_amount": round(total_amount, 2),
        "status": "pending",
        "shipping_address": new_order.shipping_address,
        "created_at": now,
        "updated_at": now
    }

    orders_db.append(created_order)
    return created_order

# 4. Update order
@app.put("/orders/{order_id}", response_model=Order)
def update_order(order_id: int, update: OrderUpdate, current_user: dict = Depends(verify_token)):
    """
    Update an existing order (status or shipping address). Requires JWT authentication.
    """
    for order in orders_db:
        if order["id"] == order_id:
            # Validate status
            if update.status and update.status not in VALID_STATUSES:
                raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}")

            # Cannot update cancelled or delivered orders
            if order["status"] in ["cancelled", "delivered"]:
                raise HTTPException(status_code=400, detail=f"Cannot update order with status '{order['status']}'")

            # Update fields
            if update.status is not None:
                order["status"] = update.status
            if update.shipping_address is not None:
                order["shipping_address"] = update.shipping_address

            order["updated_at"] = datetime.now().isoformat()
            return order

    raise HTTPException(status_code=404, detail="Order not found")

# 5. Cancel order
@app.post("/orders/{order_id}/cancel")
def cancel_order(order_id: int, current_user: dict = Depends(verify_token)):
    """
    Cancel an order. Only pending or processing orders can be cancelled. Requires JWT authentication.
    """
    for order in orders_db:
        if order["id"] == order_id:
            if order["status"] in ["shipped", "delivered", "cancelled"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot cancel order with status '{order['status']}'"
                )

            order["status"] = "cancelled"
            order["updated_at"] = datetime.now().isoformat()

            return {
                "message": "Order cancelled successfully",
                "order_id": order_id,
                "status": order["status"]
            }

    raise HTTPException(status_code=404, detail="Order not found")

# 6. Get order summary by user
@app.get("/users/{user_id}/orders/summary")
def get_user_order_summary(user_id: int, current_user: dict = Depends(verify_token)):
    """
    Get order summary for a specific user. Requires JWT authentication.
    """
    user_orders = [o for o in orders_db if o["user_id"] == user_id]

    if not user_orders:
        return {
            "user_id": user_id,
            "total_orders": 0,
            "total_spent": 0.0,
            "orders_by_status": {}
        }

    total_spent = sum(o["total_amount"] for o in user_orders)

    orders_by_status = {}
    for status in VALID_STATUSES:
        count = len([o for o in user_orders if o["status"] == status])
        if count > 0:
            orders_by_status[status] = count

    return {
        "user_id": user_id,
        "total_orders": len(user_orders),
        "total_spent": round(total_spent, 2),
        "orders_by_status": orders_by_status
    }

# 7. Delete order
@app.delete("/orders/{order_id}", status_code=204)
def delete_order(order_id: int, current_user: dict = Depends(verify_token)):
    """
    Delete an order by ID. Requires JWT authentication.
    """
    for order in orders_db:
        if order["id"] == order_id:
            orders_db.remove(order)
            return
    raise HTTPException(status_code=404, detail="Order not found")

# 8. Reset database
@app.post("/reset-db")
def reset_database():
    """
    Reset the order database to initial state.
    """
    orders_db.clear()
    orders_db.extend([
        {
            "id": 1,
            "user_id": 1,
            "items": [
                {"product_id": 1, "product_name": "Laptop", "quantity": 1, "price": 999.99},
                {"product_id": 2, "product_name": "Wireless Mouse", "quantity": 2, "price": 29.99}
            ],
            "total_amount": 1059.97,
            "status": "delivered",
            "shipping_address": "123 Main St, City, State 12345",
            "created_at": "2025-01-10T10:00:00",
            "updated_at": "2025-01-15T14:30:00"
        },
        {
            "id": 2,
            "user_id": 2,
            "items": [
                {"product_id": 4, "product_name": "Monitor", "quantity": 1, "price": 399.99}
            ],
            "total_amount": 399.99,
            "status": "pending",
            "shipping_address": "456 Oak Ave, Town, State 67890",
            "created_at": "2025-01-11T15:20:00",
            "updated_at": "2025-01-11T15:20:00"
        },
        {
            "id": 3,
            "user_id": 1,
            "items": [
                {"product_id": 3, "product_name": "USB-C Cable", "quantity": 3, "price": 12.99}
            ],
            "total_amount": 38.97,
            "status": "shipped",
            "shipping_address": "123 Main St, City, State 12345",
            "created_at": "2025-01-12T09:15:00",
            "updated_at": "2025-01-13T11:00:00"
        }
    ])
    return {"message": "Order database reset successfully"}
