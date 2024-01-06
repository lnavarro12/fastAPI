# hacer la instanciación de la base de datos
from fastapi import APIRouter, HTTPException, Path, Depends, Request, Form
from typing import Annotated
from starlette import status, responses
from models import Todos
from helpers import db_dependency
from .auth import get_current_user
from sqlalchemy import desc

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
    
    todos = db.query(Todos).filter_by(owner_id =1).order_by(desc(Todos.priority)).all()
    return templates.TemplateResponse("home.html", {"request": request, "todos": todos})

@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request, todo_id: int  = None):
    # Puedes enviar el objeto "todo" como None si estás creando uno nuevo
    return templates.TemplateResponse("todo.html", {"request": request, "todo": None})


@router.get("/delete/{todo_id}")
async def delete_todo(request: Request, todo_id: int, db: db_dependency):
    todo_model = db.query(Todos).filter_by(id=todo_id, owner_id = 1).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.query(Todos).filter_by(id=todo_id).delete()
    db.commit()
    return responses.RedirectResponse(url="/todo", status_code = status.HTTP_302_FOUND)

@router.get("/complete/{todo_id}")
async def delete_todo(request: Request, todo_id: int, db: db_dependency):
    todo = db.query(Todos).filter_by(id=todo_id).first()

    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo.complete = not todo.complete
    db.commit()
    return responses.RedirectResponse(url="/todo", status_code = status.HTTP_302_FOUND)



# When you need to receive form fields instead of JSON, you can use Form.
@router.post("/save-todo", response_class=HTMLResponse)
@router.post("/save-todo/{todo_id}", response_class=HTMLResponse)
async def save_info_todo(
        request: Request,
        db: db_dependency,
        title: str = Form(...),
        description: str = Form (...),
        priority: int = Form(...),
        todo_id: int = None
    ):

    # Si todo_id no es None, entonces es una solicitud de actualización
    if todo_id:
        todo = db.query(Todos).filter_by(id=todo_id).first()
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")

        # Actualiza los valores existentes
        todo.title = title
        todo.priority = priority
        todo.description = description

    else:

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
async def edit_todo(request: Request,
                    db : db_dependency,
                    todo_id: int = Path(gt=0)):

    # find the record in the database
    todo = db.query(Todos).filter_by(id =todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    return templates.TemplateResponse("todo.html", {"request": request, "todo": todo})


