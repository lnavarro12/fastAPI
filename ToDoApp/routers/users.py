from fastapi import APIRouter, HTTPException, Path, Depends
from typing import Annotated
from starlette import status
from models import Users
from schema import userVerification, UserUpdate, UserWithORM
from helpers import db_dependency
from .auth import get_current_user, bcrypt_context

router = APIRouter()
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/", status_code=status.HTTP_200_OK, description="Get user information", response_model=UserWithORM)
async def get_user(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    return db.query(Users).filter_by(id=user.get("id")).first()

@router.put("/change-password", status_code=status.HTTP_204_NO_CONTENT, description="Change password")
async def change_password(db: db_dependency, user: user_dependency, user_verification: userVerification):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    info_user = db.query(Users).filter_by(id=user.get("id")).first()

    if info_user is None:
        raise HTTPException(status_code=404, detail="User does not exist")
    else:
        if not bcrypt_context.verify(user_verification.password, info_user.hashed_password):
            raise HTTPException(status_code=401, detail="Error on password change")

        info_user.hashed_password = bcrypt_context.hash(user_verification.new_password)
        db.add(info_user)
        db.commit()

@router.put("/", status_code=status.HTTP_204_NO_CONTENT, description="Update user information")
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