from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from .models import products_db
from .schemas import Product, ProductCreate, ProductUpdate
from typing import Optional
import jwt
import sys
import os

# Add parent directory to path to import jwt_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from jwt_config import SECRET_KEY, ALGORITHM

app = FastAPI(
    title="Product Management API",
    description="Independent service for managing products and inventory (Requires JWT Authentication)",
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

# 1. List all products
@app.get("/products", response_model=list[Product])
def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock availability"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Limit number of results"),
    offset: Optional[int] = Query(None, ge=0, description="Offset for pagination"),
    current_user: dict = Depends(verify_token)
):
    """
    Get all products with optional filtering. Requires JWT authentication.
    """
    filtered_products = products_db

    # Apply filters
    if category:
        filtered_products = [p for p in filtered_products if p["category"].lower() == category.lower()]

    if min_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] >= min_price]

    if max_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] <= max_price]

    if in_stock is not None:
        if in_stock:
            filtered_products = [p for p in filtered_products if p["stock"] > 0]
        else:
            filtered_products = [p for p in filtered_products if p["stock"] == 0]

    # Apply pagination
    start = offset if offset is not None else 0
    end = start + limit if limit is not None else len(filtered_products)

    return filtered_products[start:end]

# 2. Get product by ID
@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int, current_user: dict = Depends(verify_token)):
    """
    Get a specific product by ID. Requires JWT authentication.
    """
    for product in products_db:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

# 3. Get product by SKU
@app.get("/products/sku/{sku}", response_model=Product)
def get_product_by_sku(sku: str, current_user: dict = Depends(verify_token)):
    """
    Get a specific product by SKU. Requires JWT authentication.
    """
    for product in products_db:
        if product["sku"] == sku:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

# 4. Create new product
@app.post("/products", response_model=Product, status_code=201)
def create_product(new_product: ProductCreate, current_user: dict = Depends(verify_token)):
    """
    Create a new product. Requires JWT authentication.
    """
    # Check for duplicate SKU
    for product in products_db:
        if product["sku"] == new_product.sku:
            raise HTTPException(status_code=400, detail="SKU already exists")

    # Generate new ID
    next_id = max(p["id"] for p in products_db) + 1 if products_db else 1

    created_product = {"id": next_id, **new_product.dict()}
    products_db.append(created_product)
    return created_product

# 5. Update product
@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, update: ProductUpdate, current_user: dict = Depends(verify_token)):
    """
    Update an existing product. Requires JWT authentication.
    """
    for product in products_db:
        if product["id"] == product_id:
            # Check for duplicate SKU if SKU is being updated
            if update.sku and update.sku != product["sku"]:
                for other_product in products_db:
                    if other_product["id"] != product_id and other_product["sku"] == update.sku:
                        raise HTTPException(status_code=400, detail="SKU already exists")

            # Update fields
            if update.name is not None:
                product["name"] = update.name
            if update.description is not None:
                product["description"] = update.description
            if update.price is not None:
                product["price"] = update.price
            if update.stock is not None:
                product["stock"] = update.stock
            if update.category is not None:
                product["category"] = update.category
            if update.sku is not None:
                product["sku"] = update.sku

            return product

    raise HTTPException(status_code=404, detail="Product not found")

# 6. Delete product
@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, current_user: dict = Depends(verify_token)):
    """
    Delete a product by ID. Requires JWT authentication.
    """
    for product in products_db:
        if product["id"] == product_id:
            products_db.remove(product)
            return
    raise HTTPException(status_code=404, detail="Product not found")

# 7. Update stock
@app.patch("/products/{product_id}/stock")
def update_stock(product_id: int, quantity: int, current_user: dict = Depends(verify_token)):
    """
    Update product stock. Use positive values to add stock, negative to reduce. Requires JWT authentication.
    """
    for product in products_db:
        if product["id"] == product_id:
            new_stock = product["stock"] + quantity

            if new_stock < 0:
                raise HTTPException(status_code=400, detail="Insufficient stock")

            product["stock"] = new_stock
            return {
                "product_id": product_id,
                "previous_stock": product["stock"] - quantity,
                "current_stock": product["stock"],
                "change": quantity
            }

    raise HTTPException(status_code=404, detail="Product not found")

# 8. Get categories
@app.get("/categories")
def get_categories(current_user: dict = Depends(verify_token)):
    """
    Get all unique product categories. Requires JWT authentication.
    """
    categories = list(set(p["category"] for p in products_db))
    return {"categories": sorted(categories)}

# 9. Reset database
@app.post("/reset-db")
def reset_database():
    """
    Reset the product database to initial state.
    """
    products_db.clear()
    products_db.extend([
        {
            "id": 1,
            "name": "Laptop",
            "description": "High-performance laptop with 16GB RAM",
            "price": 999.99,
            "stock": 50,
            "category": "Electronics",
            "sku": "LAP-001"
        },
        {
            "id": 2,
            "name": "Wireless Mouse",
            "description": "Ergonomic wireless mouse",
            "price": 29.99,
            "stock": 200,
            "category": "Accessories",
            "sku": "MOU-001"
        },
        {
            "id": 3,
            "name": "USB-C Cable",
            "description": "Fast charging USB-C cable 2m",
            "price": 12.99,
            "stock": 500,
            "category": "Accessories",
            "sku": "CAB-001"
        },
        {
            "id": 4,
            "name": "Monitor",
            "description": "27-inch 4K monitor",
            "price": 399.99,
            "stock": 30,
            "category": "Electronics",
            "sku": "MON-001"
        }
    ])
    return {"message": "Product database reset successfully"}
