from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
import schema
from models import Users
from starlette import status, responses
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from helpers import db_dependency
from dotenv import load_dotenv
import os

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

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
# Tiene como dependencia el request, porque se evaluará en las cookies si viene el access token que
# ya debio haberse generado a este punto
async def get_current_user(request:Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role : str = payload.get("role")

        if username is None or user_id is None:
            logout(request)

        return {"username": username, "id": user_id, "role": user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")


@router.post("/token", response_model=schema.Token)
async def doLogin(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                  db: db_dependency):
    user = authenticate_user(username=form_data.username, password=form_data.password, db=db)
    if not user:
        return False

    token = create_access_token(user.username,
                                user.id,
                                timedelta(60),
                                user.role
                                )

    response.set_cookie(key="access_token", value=token, httponly=True)

    return True

@router.get("/", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register", response_class=HTMLResponse)
async def register_user(request: Request, db: db_dependency,
                        email: str = Form(...), username: str = Form(...),
                        firstname: str = Form(...), lastname: str = Form(...),
                        password: str = Form(...), verify_password: str = Form(...)):

    validate_user_exist = db.query(Users).filter(Users.username==username or Users.email==email).first()
    error = False
    msg = ""
    if validate_user_exist is not None:
        error = True
        msg = "User already exist!"

    if password != verify_password:
        error = True
        msg = "Password not validate!"

    if error:
        return templates.TemplateResponse("register.html", {"request": request, "msg": msg})

    new_user = Users(
        email=email,
        username=username,
        first_name=firstname,
        last_name=lastname,
        hashed_password=bcrypt_context.hash(password),
        is_active= True
    )

    db.add(new_user)
    db.commit()

    msg = "User created successfully!"
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg , "success": True})

@router.post("/authenticate", response_class=HTMLResponse)
async def login(
                request: Request,
                db: db_dependency
                ):
    try:
        form = schema.LoginForm(request)
        await form.create_oauth_form()
        response = responses.RedirectResponse(url="/todo", status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await doLogin(response=response, form_data = form, db=db)

        if not validate_user_cookie:
            msg = "Incorrect username or password"
            return templates.TemplateResponse("login.html", {"request": request, "msg": msg, "success": False})

        return response

    except HTTPException:
        msg= "Unknown error"
        return templates.TemplateResponse("login.html", {"request": request, "msg":msg , "success": False})

@router.get("/logout")
async def logout(request: Request):
    msg = "Logout Successful"
    response = templates.TemplateResponse("login.html", {"request": request, "msg": msg})
    response.delete_cookie(key="access_token")
    return response