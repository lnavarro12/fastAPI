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

@router.get("/test")
async def test(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@router.get("/", status_code=status.HTTP_200_OK, description="Get all todos")
# Depends : Dependency injection, necesitamos hacer algo antes de ejecutar
async def read_all(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if user.get("role") != "admin":
        # pasas la base de datos en sesión
        # se escribe un query
        # se pasa la clase de l modelo que nos interesa y que queremos obtener que en este caso es todo
        return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()
    else:
        return db.query(Todos).all()

@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo_by_id(user: user_dependency,
                          db:db_dependency,
                          todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    todo_model = db.query(Todos).filter_by(id=todo_id, owner_id=user.get("id")).first()

    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency,
                      db:db_dependency,
                      todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    todo_model = Todos(**todo_request.model_dump(), owner_id= user.get("id"))

    db.add(todo_model)
    db.commit()

@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db:db_dependency,
                      todo_request: TodoRequest,
                      todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if user.get("role") != "admin":
        todo_model = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user.get("id")).first()
    else:
        todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency,db:db_dependency, todo_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if user.get("role") != "admin":
        todo_model = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user.get("id")).first()
    else:
        todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.query(Todos).filter(Todos.id == todo_id).delete()

    db.commit()



