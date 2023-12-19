from typing import Annotated
from sqlalchemy.orm import Session
from database import SessionLocal
from fastapi import Depends
def get_db():
    # db = SessionLocal(): Se crea una nueva instancia de la clase de sesión que se definió previamente con sessionmaker
    db = SessionLocal()
    try:
        #  La palabra clave yield convierte automáticamente la función en un generador en Python.
        #  En este contexto, el generador devuelve la sesión de base de datos (db) a la parte del código que llama a get_db.
        yield db
    finally:
        # finally: db.close(): Después de que el bloque de código haya terminado de ejecutarse
        # (ya sea con éxito o debido a una excepción), el bloque finally se ejecutará,
        # asegurándose de que la sesión de base de datos se cierre correctamente.
        # Esto es importante para liberar los recursos asociados con la conexión a la base de datos
        # y evitar posibles problemas de recursos.
        db.close()


# En resumen, db_dependency se utiliza como una dependencia en rutas FastAPI para inyectar la sesión de la base de datos.
db_dependency = Annotated[Session, Depends(get_db)]