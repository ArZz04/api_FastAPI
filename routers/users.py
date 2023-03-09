from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db.models.user import User, UserDB
from db.schemas.user import user_schema, users_schema
from db.client import db_client
from bson import ObjectId

from jose import jwt, JWTError
from passlib.context import CryptContext

ALGORITHM = "HS256"
SECRET = "$2y$10$eDExHEG0GSWUvXhoxWovM./wsJS38BHu69l3qouX3zKNDGdqp7pve" #karlita 2 times
security = HTTPBearer()

crypt = CryptContext(schemes=["bcrypt"])


router = APIRouter(prefix="/user",
                   tags=["user"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

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

@router.get("/", response_model=list[User]) #TESTED
async def users(token: HTTPAuthorizationCredentials = Depends(security)):
    payload = await verify_token(token.credentials)
    return users_schema(db_client.users.find())


@router.get("/{id}")  # Path #TESTED
async def user(id: str, token: HTTPAuthorizationCredentials = Depends(security)):
    payload = await verify_token(token.credentials)
    return search_user("_id", ObjectId(id))


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED) #TESTED
async def user(user: UserDB, token: HTTPAuthorizationCredentials = Depends(security)):
    payload = await verify_token(token.credentials)

    if type(search_user("email", user.email)) == User:
       raise HTTPException(
           status.HTTP_404_NOT_FOUND, detail="El usuario ya existe")

    user_dict = dict(user)
    del user_dict['id']

    password_dict = {"password": user_dict["password"]}
    encoded_password = jwt.encode(password_dict, SECRET, algorithm=ALGORITHM)
    user_dict["password"] = encoded_password


    id = db_client.users.insert_one(user_dict).inserted_id

    new_user = user_schema(db_client.users.find_one({"_id": id}))

    return User(**new_user)


@router.put("/", response_model=User)
async def update_user(user: UserDB, token: HTTPAuthorizationCredentials = Depends(security)):
    payload = await verify_token(token.credentials)

    try:

        user_dict = dict(user)
        del user_dict["id"]

        password_dict = {"password": user_dict["password"]}
        encoded_password = jwt.encode(password_dict, SECRET, algorithm=ALGORITHM)
        user_dict["password"] = encoded_password

        db_client.users.find_one_and_replace(
            {"_id": ObjectId(user.id)}, user_dict)
    except:
        return {"error": "No se ha actualizado el usuario"}    
    
    return search_user("_id", ObjectId(user.id))


@router.delete("/{id}")
async def user(id: str, token: HTTPAuthorizationCredentials = Depends(security)):
    payload = await verify_token(token.credentials)

    found = db_client.users.find_one_and_delete({"_id": ObjectId(id)})

    if not found:
        return {"error": "No se ha eliminado el usuario"}

# HELPER

def search_user(field: str, key):
    try:
        user = db_client.users.find_one({field: key})
        return User(**user_schema(user))
    except:
        return {"error": "No se ha encontrado el usuario"}