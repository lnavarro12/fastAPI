from fastapi import FastAPI, Path, Query, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

class Book:
    id: int
    title: str
    author: str
    description: str
    rating:int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date

class BookRequest(BaseModel):
    # esta campo es opcional, puede ser entero o puede ser None
    id: Optional[int] = Field(None, title="id is not needed")
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_lenght=1, max_lenght=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1900)

    class Config:
        # Puedes dejar un ejemplo del post que has de seguir
        json_schema_extra = {
            "example": {
                "title": "A new book",
                "author": "codingwithroby",
                "description": "a new description",
                "rating": 5,
                "published_date": 2012
            }
        }

BOOKS = [
    Book(1, "Computer Science Pro", "CodingWithRobbie", "Book of code", 5, 2015),
    Book(2, "New Earth Project", "David Moitet", "very nice Reseña del libro", 4, 2016),
    Book(3, "Neurociencia del Cuerpo", "Nazareth Perales Castellanos ", "nice Reseña del libro", 4, 2017),
    Book(4, "La Teoría del Amor", "Ali Hazelwood", "buh Reseña del libro", 3, 2017),
    Book(5, "Los años de peregrinación del chico sin color", "Murakami, Haruki", "buh Reseña del libro", 1, 2021),
]

@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS

@app.get("/books/", status_code=status.HTTP_200_OK)
async def find_book_by_rating(rating:int):
    result = []
    for b in BOOKS:
        if b.rating == rating:
            print("hola mundo")
            result.append(b)
    return result

@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id:int = Path(gt=0, title="The ID of the item to get")):
    for b in BOOKS:
        if b.id == book_id:
            return b

    raise HTTPException(status_code=404, detail="Item not found")

@app.get("/books/publish/", status_code=status.HTTP_200_OK)

async def find_books_by_year(book_year:int = Query(gt=1900 )):
    results = []
    for b in BOOKS:
        if b.published_date == book_year:
            results.append(b)
    return results

@app.post("/books", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    # converting the request to Book object
    new_book = Book(**book_request.model_dump())
    # model_dump -> convierte un modelo a un diccionario
    BOOKS.append(find_book_id(new_book))

# función que retorna el último id de la lista de libros
def find_book_id(book:Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book

@app.put("/books", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = book

            return book

    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/books/{book_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id:int=Path(gt=0)):
    book_change = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.remove(BOOKS[i])
            book_change = True
            break
    if not book_change:
        raise HTTPException(status_code=404, detail="Item not found")