from fastapi import FastAPI
from routers import users, jwt_auth_users, product, get_info

app = FastAPI()

app.include_router(users.router)
app.include_router(jwt_auth_users.router)
app.include_router(product.router)
app.include_router(get_info.router)

@app.get("/")
async def root():
    return "API works correctly"

@app.get("/info")
async def url():
    return {'INICIAR SERVIDOR' : "uvicorn main:app --reload"}

# Inicia el server: uvicorn main:app --reload
# Detener el server: CTRL+C

# Documentación con Swagger: http://127.0.0.1:8000/docs
# Documentación con Redocly: http://127.0.0.1:8000/redoc
