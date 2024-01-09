# este archivo principal nos permite crear la aplicación de fastApi
# hacer la instanciación de la base de datos
from fastapi import FastAPI
import models
from database import engine
from routers import auth, todos, users
from starlette import status
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

app = FastAPI()

# redireccionar las direcciones a la raiz del proyecto que es todo
@app.get("/")
async def root():
    return RedirectResponse("/todo", status_code=status.HTTP_302_FOUND)

# Cuando se corra la aplicación se creará automaticamente una base de datos en la ubicación  especificada en la URL
# tambien se crean las tablas tal como se definieron en el modelo
models.Base.metadata.create_all(bind=engine)

# en FastAPI para servir archivos estáticos desde el directorio "static"
# en app una instancia de la clase FastAPI.
# crea un objeto StaticFiles que sirve archivos estáticos desde el directorio 
# especificado ("static" en este caso).

# monta la aplicación de archivos estáticos en una ruta específica ("/static"). 
# La ruta "/static" se usará para acceder a los archivos estáticos, 
# y la aplicación de archivos estáticos se encargará de servir esos 
# archivos desde el directorio especificado.
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(todos.router, prefix="/todo", tags=["Todos"])
app.include_router(users.router, prefix="/user", tags=["Users"])
