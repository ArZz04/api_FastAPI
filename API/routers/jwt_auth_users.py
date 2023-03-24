from fastapi import APIRouter, Depends, HTTPException, status, FastAPI
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from bson import ObjectId

from db.client import db_client
from db.models.user import User, UserDB

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 999999999
SECRET = "$2y$10$eDExHEG0GSWUvXhoxWovM./wsJS38BHu69l3qouX3zKNDGdqp7pve" #karlita 2 times

router = APIRouter(responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

#prefix="/auth",
                   #tags=["auth"],
                   

oauth2 = OAuth2PasswordBearer(tokenUrl='login')

crypt = CryptContext(schemes=["bcrypt"])


#FUNCTIONS

def search_user_db(username: str):
    user_dict = db_client.users.find_one({"username": username})
    if user_dict:
        return UserDB(**user_dict)
    

def search_user_(username: str):
    user_dict = db_client.users.find_one({"username": username})
    if user_dict:
        return User(**user_dict)

async def auth_user(token: str = Depends(oauth2)):

    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticación inválidas",
        headers={"WWW-Authenticate": "Bearer"})

    try:
        username = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("sub")
        if username is None:
            raise exception

    except JWTError:
        raise exception

    return search_user_(username)
    
async def current_user(user: User = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo")
    
    return user
# PATHS

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = search_user_db(form.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no es correcto")

    passw = jwt.decode(user.password, SECRET, algorithms=[ALGORITHM]).get("password")

    if form.password != passw:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña no es correcta")

    access_token = {"sub":user.username, 
                    "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION),
                    "pass": "2516"}

    return {"access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM), "token_type": "bearer"}


@router.get("/me")
async def me(user: User = Depends(current_user)):
    return user