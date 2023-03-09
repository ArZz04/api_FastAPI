from fastapi import APIRouter, HTTPException, status
from db.models.product import Product
from db.schemas.product import product_schema, products_schema
from db.client import db_client
from bson import ObjectId

router = APIRouter(prefix="/product",
                   tags=["product"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

@router.get("/", response_model=list[Product])
async def products():
    return products_schema(db_client.products.find())

@router.get("/{id}")  # Path
async def product(id: str):
    return search_product("_id", ObjectId(id))

@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def product(product: Product):

    if type(search_product("ean", product.ean)) == Product:
       raise HTTPException(
           status.HTTP_404_NOT_FOUND, detail="El producto ya existe")

    product_dict = dict(product)
    del product_dict['id']

    id = db_client.products.insert_one(product_dict).inserted_id

    new_product = product_schema(db_client.products.find_one({"_id": id}))

    return Product(**new_product)


@router.put("/", response_model=Product)
async def product_update(product: Product):

    try:

        product_dict = dict(product)
        del product_dict["id"]

        db_client.products.find_one_and_replace(
            {"_id": ObjectId(product.id)}, product_dict)
    
    except:
        return {"error": "No se ha actualizado el producto"}

    return search_product("_id", ObjectId(product.id))


@router.delete("/{id}")
async def product(id: str):

    found = db_client.products.find_one_and_delete({"_id": ObjectId(id)})

    if not found:
        return {"error": "No se ha eliminado el producto"}

# HELPER

def search_product(field: str, key):
    try:
        product = db_client.products.find_one({field: key})
        return Product(**product_schema(product))
    except:
        return {"error": "No se ha encontrado el producto"}
