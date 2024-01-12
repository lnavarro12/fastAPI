from fastapi import APIRouter, HTTPException, Depends, Request, Form
from typing import Annotated
from starlette import status
from models import Users
from schema import userVerification, UserUpdate, UserWithORM
from helpers import db_dependency
from starlette.responses import HTMLResponse, RedirectResponse
from .auth import get_current_user, bcrypt_context
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter()
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/", status_code=status.HTTP_200_OK, description="Get user information", response_model=UserWithORM)
async def get_user(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    return db.query(Users).filter_by(id=user.get("id")).first()

@router.get("/change-password", response_class=HTMLResponse)
async def change_password(request: Request):
    user = await get_current_user(request)
    return templates.TemplateResponse("change-password.html", {"request": request, "user": user if user is not None else None})

@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT, description="Change password")
async def change_password(db: db_dependency,
                          request: Request,
                          username: str = Form(default=None),
                          current_password: str = Form(default=None),
                          new_password: str = Form(...),
                          confirm_password: str = Form(default=None)
                          ):

    user = await get_current_user(request)

    if user is None:
        # validate the username and password
        info_user = db.query(Users).filter_by(username=username).first()

        if info_user is None or not bcrypt_context.verify(current_password, info_user.hashed_password):
            msg = "Invalid username or password"
            return templates.TemplateResponse("change-password.html", {"request": request, "msg": msg})

        else:
            info_user.hashed_password = bcrypt_context.hash(new_password)
            db.add(info_user)
            db.commit()
            return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    else:

        if new_password != confirm_password:
            msg = "Passwords do not match"
            return templates.TemplateResponse("change-password.html", {"request": request, "msg": msg})

        # validate the username and password
        info_user = db.query(Users).filter_by(id=user.get("id")).first()
        if info_user is None:
            return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

        info_user.hashed_password = bcrypt_context.hash(new_password)
        db.add(info_user)
        db.commit()
        return RedirectResponse(url="/todo", status_code=status.HTTP_302_FOUND)

@router.put("/", status_code=status.HTTP_204_NO_CONTENT,
            description="Update user information")
async def update_user_info(db: db_dependency, user: user_dependency, user_request: UserUpdate):
    
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    info_user = db.query(Users).filter_by(id=user.get("id")).first()

    if info_user is None:
        raise HTTPException(status_code=404, detail="User does not exist")
    else:
        
        if user_request.email:
            info_user.email = user_request.email
        
        if user_request.first_name:
            info_user.first_name = user_request.first_name
        
        if user_request.last_name:
            info_user.last_name = user_request.last_name
        
        if user_request.role:
            info_user.role = user_request.role
        
        if user_request.phone_number:
            info_user.phone_number = user_request.phone_number
        
        db.add(info_user)
        db.commit()