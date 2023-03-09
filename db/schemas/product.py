
def product_schema(product) -> dict:
    return {"id": str(product["_id"]),
            "ean": product["ean"],
            "product_name": product["product_name"],
            "price": product["price"]
            }

def products_schema(products) -> list:
    return [product_schema(product) for product in products]