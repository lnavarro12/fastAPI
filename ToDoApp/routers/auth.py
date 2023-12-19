from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
import schema
from models import Users
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from helpers import db_dependency
from dotenv import load_dotenv
import os

router = APIRouter()

# Load .env file
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')

#La instancia oauth2_bearer creada con OAuth2PasswordBearer se
# utilizará luego como dependencia en rutas que requieren autenticación mediante token de acceso.

# Cuando un cliente realiza una solicitud a una ruta protegida,
# el token de acceso se espera que esté presente en el encabezado
# de autorización de la solicitud. La instancia oauth2_bearer
# se encargará de analizar y validar ese token.

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

# functions
def authenticate_user(username:str, password: str, db):
    user = db.query(Users).filter_by(username=username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username:str, user_id: int, expires_delta: timedelta, role: str):

    encode = {"sub": username, "id": user_id, "role": role}
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

# Cada vez que se necesite seguridad en los endpoints, se llamará a esta función
# Para verificar el token que el cliente envió con el OAuth
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role : str = payload.get("role")

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")

        return {"username": username, "id": user_id, "role": user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")


@router.post("/", status_code=status.HTTP_201_CREATED, description="Create an user")
async def create_user(db: db_dependency,
                      create_user_request: schema.CreateUserRequest):
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True
    )
    db.add(create_user_model)
    db.commit()

@router.post("/token", response_model=schema.Token)
async def doLogin(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                  db: db_dependency):
    user = authenticate_user(username=form_data.username, password=form_data.password, db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")

    token = create_access_token(user.username, user.id, timedelta(minutes=20), user.role)

    return {"access_token":token, "token_type": "bearer"}
