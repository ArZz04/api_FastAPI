from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db.models.product import Product
from db.schemas.product import product_schema, products_schema
from db.client import db_client
from bson import ObjectId
from jose import JWTError, jwt

security = HTTPBearer()
router = APIRouter(prefix="/product",
                   tags=["product"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

SECRET = "$2y$10$eDExHEG0GSWUvXhoxWovM./wsJS38BHu69l3qouX3zKNDGdqp7pve" #karlita 2 times

# función que verifica el token
async def verify_token(token: str):
    try:
        # decodifica el token y verifica la firma
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        # aquí puedes verificar el contenido del payload si lo deseas
    except JWTError:
        # si hay un error en la verificación, se lanza una excepción
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    # si todo está bien, devuelve el payload
    return payload

@router.get("/", response_model=list[Product])
async def products(token: HTTPAuthorizationCredentials = Depends(security)):
    payload = await verify_token(token.credentials)

    return products_schema(db_client.products.find())

@router.get("/{ean}")  # Path
async def product(ean: str, token: HTTPAuthorizationCredentials = Depends(security)):
    payload = await verify_token(token.credentials)

    return search_product("ean", ean)

@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def product(product: Product, token: HTTPAuthorizationCredentials = Depends(security)):
    payload = await verify_token(token.credentials)

    if type(search_product("ean", product.ean)) == Product:
       raise HTTPException(
           status.HTTP_404_NOT_FOUND, detail="El producto ya existe")

    product_dict = dict(product)
    del product_dict['id']

    id = db_client.products.insert_one(product_dict).inserted_id

    new_product = product_schema(db_client.products.find_one({"_id": id}))

    return Product(**new_product)


@router.put("/", response_model=Product)
async def product_update(product: Product, token: HTTPAuthorizationCredentials = Depends(security)):
    payload = await verify_token(token.credentials)

    try:

        product_dict = dict(product)
        del product_dict["id"]

        db_client.products.find_one_and_replace(
            {"_id": ObjectId(product.id)}, product_dict)
    
    except:
        return {"error": "No se ha actualizado el producto"}

    return search_product("_id", ObjectId(product.id))


@router.delete("/{ean}")
async def product(ean: str, token: HTTPAuthorizationCredentials = Depends(security)):
    payload = await verify_token(token.credentials)

    found = db_client.products.find_one_and_delete({"ean": ean})

    if not found:
        return {"error": "No se ha eliminado el producto"}

# HELPER

def search_product(field: str, key):
    try:
        product = db_client.products.find_one({field: key})
        return Product(**product_schema(product))
    except:
        return {"error": "No se ha encontrado el producto"}
