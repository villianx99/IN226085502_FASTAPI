from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI(title="E-Commerce Products API")

# ---------------- PRODUCTS DATA ----------------

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "USB-C Hub", "price": 799, "category": "Electronics", "in_stock": True},
    {"id": 3, "name": "Desk Lamp", "price": 199, "category": "Home Office", "in_stock": False},
    {"id": 4, "name": "Notebook", "price": 50, "category": "Stationery", "in_stock": False},
    {"id": 5, "name": "Laptop Stand", "price": 35.99, "category": "Accessories", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 89.99, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 59.99, "category": "Electronics", "in_stock": True},
]

cart = []
orders = []
feedback = []

# ---------------- BASIC ROUTES ----------------

@app.get("/")
def root():
    return {"message": "Welcome to the E-Commerce Products API 🛒"}


@app.get("/products")
def get_products():
    return {"total": len(products), "products": products}

@app.get("/products/sort-by-category")
def sort_by_category():

    sorted_products = sorted(
        products,
        key=lambda p: (p["category"].lower(), p["price"])
    )

    return {
        "message": "Sorted by category then price",
        "products": sorted_products
    }

@app.get("/products/browse")
def browse_products(
    keyword: Optional[str] = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 4
):

    result = products

    #  1. SEARCH
    if keyword:
        result = [
            p for p in result
            if keyword.lower() in p["name"].lower()
        ]

    #  sort validation
    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}

    #  2. SORT
    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda p: p[sort_by], reverse=reverse)

    #  3. PAGINATION
    total_found = len(result)
    total_pages = (total_found + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    paginated = result[start:end]

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total_found,
        "total_pages": total_pages,
        "products": paginated
    }

@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return {"name": p["name"], "price": p["price"]}
    raise HTTPException(status_code=404, detail="Product not found")


# ---------------- CATEGORY ----------------

@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):
    filtered = [p for p in products if p["category"].lower() == category_name.lower()]

    if not filtered:
        return {"error": "No products found in this category"}

    return {"category": category_name, "total": len(filtered), "products": filtered}


# ---------------- INSTOCK ----------------

@app.get("/products/instock")
def get_instock_products():
    instock = [p for p in products if p["in_stock"]]

    return {"count": len(instock), "products": instock}


# ---------------- SEARCH ----------------

@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    matched = [p for p in products if keyword.lower() in p["name"].lower()]

    if not matched:
        return {"message": "No products matched your search"}

    return {"keyword": keyword, "total": len(matched), "products": matched}


# ---------------- FILTER ----------------

@app.get("/products/filter")
def filter_products(
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        category: Optional[str] = None):

    result = products

    if min_price is not None:
        result = [p for p in result if p["price"] >= min_price]

    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]

    if category is not None:
        result = [p for p in result if p["category"].lower() == category.lower()]

    return result

@app.get("/products/sort")
def sort_products(sort_by: str = "price", order: str = "asc"):

    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}

    reverse = True if order == "desc" else False

    sorted_products = sorted(products, key=lambda p: p[sort_by], reverse=reverse)

    return {
        "sort_by": sort_by,
        "order": order,
        "products": sorted_products
    }

from math import ceil

@app.get("/products/page")
def paginate_products(page: int = 1, limit: int = 2):

    start = (page - 1) * limit
    end = start + limit

    paginated = products[start:end]

    total_pages = ceil(len(products) / limit)

    return {
        "page": page,
        "limit": limit,
        "total_products": len(products),
        "total_pages": total_pages,
        "products": paginated
    }


# ---------------- DEALS ----------------

@app.get("/products/deals")
def get_deals():
    best_deal = min(products, key=lambda p: p["price"])
    premium_pick = max(products, key=lambda p: p["price"])

    return {"best_deal": best_deal, "premium_pick": premium_pick}


# ---------------- AUDIT ----------------

@app.get("/products/audit")
def products_audit():

    total_products = len(products)

    in_stock_count = sum(1 for p in products if p["in_stock"])

    out_of_stock_names = [p["name"] for p in products if not p["in_stock"]]

    total_stock_value = sum(p["price"] * 10 for p in products if p["in_stock"])

    most_expensive = max(products, key=lambda p: p["price"])

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_names": out_of_stock_names,
        "total_stock_value": total_stock_value,
        "most_expensive": {"name": most_expensive["name"], "price": most_expensive["price"]}
    }


# ---------------- ADD PRODUCT ----------------

class Product(BaseModel):
    name: str
    price: float
    category: str
    in_stock: bool


@app.post("/products", status_code=status.HTTP_201_CREATED)
def add_product(product: Product):

    for p in products:
        if p["name"].lower() == product.name.lower():
            raise HTTPException(status_code=400, detail="Product already exists")

    new_id = len(products) + 1

    new_product = {
        "id": new_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }

    products.append(new_product)

    return {"message": "Product added", "product": new_product}


# ---------------- UPDATE PRODUCT ----------------

@app.put("/products/{product_id}")
def update_product(product_id: int, price: Optional[int] = None, in_stock: Optional[bool] = None):

    for p in products:

        if p["id"] == product_id:

            if price is not None:
                p["price"] = price

            if in_stock is not None:
                p["in_stock"] = in_stock

            return {"message": "Product updated", "product": p}

    raise HTTPException(status_code=404, detail="Product not found")


# ---------------- DELETE PRODUCT ----------------

@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    for i, p in enumerate(products):

        if p["id"] == product_id:
            deleted_name = p["name"]
            products.pop(i)

            return {"message": f"Product '{deleted_name}' deleted"}

    raise HTTPException(status_code=404, detail="Product not found")


# ---------------- DISCOUNT ----------------

@app.put("/products/discount")
def apply_discount(category: str, discount_percent: int):

    if discount_percent < 1 or discount_percent > 99:
        return {"error": "discount_percent must be between 1 and 99"}

    updated_products = []

    for p in products:

        if p["category"].lower() == category.lower():

            new_price = int(p["price"] * (1 - discount_percent / 100))
            p["price"] = new_price

            updated_products.append({"name": p["name"], "new_price": new_price})

    if not updated_products:
        return {"message": f"No products found in category '{category}'"}

    return {"updated_count": len(updated_products), "products": updated_products}


# ---------------- FEEDBACK ----------------

class CustomerFeedback(BaseModel):
    customer_name: str
    product_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):

    feedback.append(data.dict())

    return {"message": "Feedback submitted", "total_feedback": len(feedback)}


# ---------------- ORDERS ----------------

class Order(BaseModel):
    customer_name: str
    product_id: int
    quantity: int


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

@app.get("/orders/search")
def search_orders(customer_name: str):

    matched = [
        order for order in orders
        if customer_name.lower() in order["customer_name"].lower()
    ]

    if not matched:
        return {
            "message": f"No orders found for '{customer_name}'"
        }

    return {
        "customer_name": customer_name,
        "total_found": len(matched),
        "orders": matched
    }

@app.get("/orders/page")
def paginate_orders(page: int = 1, limit: int = 3):

    total_orders = len(orders)
    total_pages = (total_orders + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    paginated_orders = orders[start:end]

    return {
        "page": page,
        "limit": limit,
        "total_orders": total_orders,
        "total_pages": total_pages,
        "orders": paginated_orders
    }

@app.get("/orders/{order_id}")
def get_order(order_id: int):

    for order in orders:
        if order["id"] == order_id:
            return order

    raise HTTPException(status_code=404, detail="Order not found")


@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):

    for order in orders:

        if order["id"] == order_id:
            order["status"] = "confirmed"
            return order

    raise HTTPException(status_code=404, detail="Order not found")


# ---------------- CART SYSTEM ----------------

@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int):

    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")

    # Check if already in cart
    existing_item = next((item for item in cart if item["product_id"] == product_id), None)

    if existing_item:
        existing_item["quantity"] += quantity
        existing_item["subtotal"] = existing_item["quantity"] * existing_item["unit_price"]

        return {
            "message": "Cart updated",
            "cart_item": existing_item
        }

    subtotal = product["price"] * quantity

    cart_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": subtotal
    }

    cart.append(cart_item)

    return {
        "message": "Added to cart",
        "cart_item": cart_item
    }


@app.get("/cart")
def view_cart():

    grand_total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }

@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):

    for i, item in enumerate(cart):

        if item["product_id"] == product_id:
            removed = cart.pop(i)

            return {
                "message": f"{removed['product_name']} removed from cart"
            }

    raise HTTPException(status_code=404, detail="Item not found in cart")

class Checkout(BaseModel):
    customer_name: str
    delivery_address: str


@app.post("/cart/checkout")
def checkout(data: Checkout):

 if not cart:
    raise HTTPException(
        status_code=400,
        detail="CART_EMPTY"
    )

    placed_orders = []
    grand_total = 0

    for item in cart:

        order_id = len(orders) + 1

        order = {
            "order_id": order_id,
            "customer_name": data.customer_name,
            "delivery_address": data.delivery_address,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "subtotal": item["subtotal"]
        }

        orders.append(order)
        placed_orders.append(order)

        grand_total += item["subtotal"]

    cart.clear()

    return {
        "message": "Checkout successful",
        "orders_placed": len(placed_orders),
        "grand_total": grand_total
    }

@app.get("/orders")
def get_orders():

    return {
        "total_orders": len(orders),
        "orders": orders
    }

