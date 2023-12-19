from pydantic import BaseModel, Field
from typing import Optional

class userVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)
class CreateUserRequest(BaseModel):
    username:str
    email: str
    first_name: str
    last_name: str
    password:str
    role: str

class Token(BaseModel):
    access_token : str
    token_type: str

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: Optional[str] = Field(min_length=3, max_length=100)
    priority: int = Field(5, gt=0, lt=6)
    complete: bool

