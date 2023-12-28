# hacer la instanciación de la base de datos
from fastapi import APIRouter, HTTPException, Path, Depends, Request
from typing import Annotated
from starlette import status
from models import Todos
from schema import TodoRequest
from helpers import db_dependency
from .auth import get_current_user

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter()

user_dependency = Annotated[dict, Depends(get_current_user)]

# Esta línea devuelve una instancia de TemplateResponse, 
# que generalmente se utiliza para renderizar plantillas 
# HTML en una aplicación web. 
@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    return templates.TemplateResponse("add-todo.html", {"request": request})

@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request):
    return templates.TemplateResponse("add-todo.html", {"request": request})


