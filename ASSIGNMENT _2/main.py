from fastapi import FastAPI

app = FastAPI(title="E-Commerce Products API")

products = [
    {"id": 1, "name": "Wireless Mouse",       "price": 499, "category": "Electronics",  "in_stock": True},
    {"id": 2, "name": "USB-C Hub",            "price": 799, "category": "Electronics",  "in_stock": True},
    {"id": 3, "name": "Desk Lamp",            "price": 199, "category": "Home Office",  "in_stock": False},
    {"id": 4, "name": "Notebook",             "price":  50, "category": "Stationery",   "in_stock": False},
    # New products (IDs 5, 6, 7)
    {"id": 5, "name": "Laptop Stand",         "price": 35.99, "category": "Accessories",  "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard",  "price": 89.99, "category": "Electronics",  "in_stock": True},
    {"id": 7, "name": "Webcam",               "price": 59.99, "category": "Electronics",  "in_stock": True},
]


@app.get("/")
def root():
    return {"message": "Welcome to the E-Commerce Products API 🛒"}


@app.get("/products")
def get_products():
    return {
        "total": len(products),
        "products": products,
    }


@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):
    filtered = [p for p in products if p["category"].lower() == category_name.lower()]
    if not filtered:
        return {"error": "No products found in this category"}
    return {
        "category": category_name,
        "total": len(filtered),
        "products": filtered,
    }


@app.get("/products/instock")
def get_instock_products():
    instock = [p for p in products if p["in_stock"] is True]
    return {
        "count": len(instock),
        "in_stock_products": instock,
    }


@app.get("/store/summary")
def store_summary():
    in_stock_count   = sum(1 for p in products if p["in_stock"] is True)
    out_stock_count  = sum(1 for p in products if p["in_stock"] is False)
    unique_categories = list(set(p["category"] for p in products))

    return {
        "store_name":      "My E-commerce Store",
        "total_products":  len(products),
        "in_stock":        in_stock_count,
        "out_of_stock":    out_stock_count,
        "categories":      unique_categories,
    }


@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    matched = [p for p in products if keyword.lower() in p["name"].lower()]
    if not matched:
        return {"message": "No products matched your search"}
    return {
        "keyword":  keyword,
        "total":    len(matched),
        "products": matched,
    }


@app.get("/products/deals")
def get_deals():
    best_deal    = min(products, key=lambda p: p["price"])
    premium_pick = max(products, key=lambda p: p["price"])
    return {
        "best_deal":    best_deal,
        "premium_pick": premium_pick,
    }


from typing import Optional

@app.get("/products/filter")
def filter_products(
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    category: Optional[str] = None
):
    result = products

    if min_price is not None:
        result = [p for p in result if p["price"] >= min_price]

    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]

    if category is not None:
        result = [p for p in result if p["category"] == category]

    return result

@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return {
                "name": p["name"],
                "price": p["price"]
            }
    return {"error": "Product not found"}


from pydantic import BaseModel, Field
from typing import Optional

feedback = []

class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)


@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    feedback.append(data.dict())

    return {
        "message": "Feedback submitted successfully",
        "feedback": data,
        "total_feedback": len(feedback)
    }

@app.get("/products/summary")
def product_summary():
    total_products = len(products)
    in_stock_count = sum(1 for p in products if p["in_stock"] == True)
    out_of_stock_count = sum(1 for p in products if p["in_stock"] == False)

    most_expensive = max(products, key=lambda p: p["price"])
    cheapest = min(products, key=lambda p: p["price"])

    categories = list(set(p["category"] for p in products))

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        },
        "cheapest": {
            "name": cheapest["name"],
            "price": cheapest["price"]
        },
        "categories": categories
    }

from pydantic import BaseModel, Field
from typing import List

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem] = Field(..., min_items=1)


@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:

        product = next((p for p in products if p["id"] == item.product_id), None)

        if not product:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })
            continue

        if not product["in_stock"]:
            failed.append({
                "product_id": item.product_id,
                "reason": f'{product["name"]} is out of stock'
            })
            continue

        subtotal = product["price"] * item.quantity
        grand_total += subtotal

        confirmed.append({
            "product": product["name"],
            "qty": item.quantity,
            "subtotal": subtotal
        })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }

# ---------- Order Status Tracker ----------

orders = []

from pydantic import BaseModel, Field

class Order(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1)


# POST /orders  → new order (status = pending)
@app.post("/orders")
def create_order(order: Order):

    order_id = len(orders) + 1

    new_order = {
        "id": order_id,
        "customer_name": order.customer_name,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "status": "pending"
    }

    orders.append(new_order)

    return new_order


# GET /orders/{order_id}
@app.get("/orders/{order_id}")
def get_order(order_id: int):

    for order in orders:
        if order["id"] == order_id:
            return order

    return {"error": "Order not found"}


# PATCH /orders/{order_id}/confirm
@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):

    for order in orders:
        if order["id"] == order_id:
            order["status"] = "confirmed"
            return order

    return {"error": "Order not found"}