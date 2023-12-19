# crearemos nuestro modelo para el archivo database.py
# este modelo define las tablas que se usaran
from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)

class Todos(Base):
    # es una manera que tiene SQLalchemy para saber como nombrar la tabla dentro de la base de datos
    __tablename__ = "todos"

    # se definen las columnas de la tabla y sus caracteristicas
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))