from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class userVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)
    
class UserBase(BaseModel):
    username:str 
    email: EmailStr
    first_name: str
    last_name: str
    password:str
    role: str
    phone_number: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr]   = None
    first_name: Optional[str]  = None
    last_name: Optional[str]  = None
    role: Optional[str]  = None
    phone_number: Optional[str] = None

class Token(BaseModel):
    access_token : str
    token_type: str

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: Optional[str] = Field(min_length=3, max_length=100)
    priority: int = Field(5, gt=0, lt=6)
    complete: bool

class UserWithORM(UserUpdate):
    class Config:
        orm_mode = True
