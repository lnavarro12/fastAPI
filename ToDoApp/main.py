# este archivo principal nos permite crear la aplicación de fastApi
# hacer la instanciación de la base de datos
from fastapi import FastAPI
import models
from database import engine
from routers import auth, todos, users

app = FastAPI()

# Cuando se corra la aplicación se creará automaticamente una base de datos en la ubicación  especificada en la URL
# tambien se crean las tablas tal como se definieron en el modelo
models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(todos.router, prefix="/todo", tags=["Todos"])
app.include_router(users.router, prefix="/user", tags=["Users"])
