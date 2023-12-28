# hacer la instanciación de la base de datos
from fastapi import APIRouter, HTTPException, Path, Depends, Request, Form
from typing import Annotated
from starlette import status, responses
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
async def read_all_by_user(request: Request, db: db_dependency):
    
    todos = db.query(Todos).filter_by(owner_id =1).all()
    return templates.TemplateResponse("home.html", {"request": request, "todos": todos})

@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    return templates.TemplateResponse("add-todo.html", {"request": request})

# When you need to receive form fields instead of JSON, you can use Form.
@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(request: Request, db: db_dependency, title: Annotated[str, Form()], 
                      description: Annotated[str, Form()], 
                      priority: Annotated[int, Form()]):
    
    todo_model = Todos(
        title = title,
        description = description,
        priority = priority,
        owner_id = 1,
        complete = False
    )
    
    db.add(todo_model)
    db.commit()
    
    return responses.RedirectResponse(url="/todo", status_code=status.HTTP_302_FOUND)

@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request, db : db_dependency, todo_id: int = Path(gt=0)):
    return templates.TemplateResponse("add-todo.html", {"request": request})


