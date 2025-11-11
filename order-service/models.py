from datetime import datetime

# Order service database
orders_db = [
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
]
