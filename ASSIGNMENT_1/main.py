from fastapi import FastAPI

app = FastAPI(title="E-Commerce Products API")

products = [
    {"id": 1, "name": "Wireless Mouse",       "price": 29.99, "category": "Electronics",  "in_stock": True},
    {"id": 2, "name": "USB-C Hub",            "price": 49.99, "category": "Electronics",  "in_stock": True},
    {"id": 3, "name": "Desk Lamp",            "price": 19.99, "category": "Home Office",  "in_stock": False},
    {"id": 4, "name": "Notebook",             "price":  5.99, "category": "Stationery",   "in_stock": False},
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
