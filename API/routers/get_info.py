from fastapi import APIRouter, status
from db.models.product import Product
from db.schemas.product import product_schema
from db.client import db_client

router = APIRouter(prefix="/get_info",
                   tags=["get_info"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "Not Found"}})

@router.get("/{ean}")  # Path
async def product(ean: str):

    return search_product("ean", ean)

def search_product(field: str, key):
    try:
        product = db_client.products.find_one({field: key})
        return Product(**product_schema(product))
    except:
        return {"error": "No se ha encontrado el producto"}
