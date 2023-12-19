from fastapi import Body, FastAPI

# variable de nuestra aplicación
app = FastAPI()

BOOKS = [
    {
        "id": 1,
        "title": "Title 1",
        "author": "Author 5",
        "category": "math"
    },{
        "id": 2,
        "title": "Title 2",
        "author": "Author 2",
        "category": "Science"
    },{
        "id": 3,
        "title": "Title 3",
        "author": "Author 3",
        "category": "Arts"
    },{
        "id": 4,
        "title": "Title 4",
        "author": "Author 4",
        "category": "math"
    },{
        "id": 5,
        "title": "Title 5",
        "author": "Author 5",
        "category": "Science"
    },{
        "id": 6,
        "title": "Title 6",
        "author": "Author 6",
        "category": "Arts"
    }
]


@app.get("/books/")
async def read_all_books():
    return BOOKS

@app.post("/books/add_book")
async def create_book(add_book=Body()):
    BOOKS.append(add_book)
    return BOOKS

@app.put("/books/{book_id}")
async def update_book(book_id:int, book=Body()):
    for b in BOOKS:
        if b.get("id") == book_id:
            b["title"] = book.get("title") if book.get("title") is not None else b.get("title")
            b["author"] = book.get("author") if book.get("author") is not None else b.get("author")
            b["category"] = book.get("category") if book.get("category") is not None else b.get("category")
    return "Actualizado"

@app.delete("/books/{book_id}")
async def delete_book(book_id: int):
    #for b in BOOKS:
    #    if b.get("id") == book_id:
    #        BOOKS.remove(b)
    #        break
    for i in range(len(BOOKS)):
        if BOOKS[i].get("id") == book_id:
            BOOKS.pop(i)
            break
    return "eliminado"

@app.get("/book/{book_title}")
async def read_book(book_title: str):
    for b in BOOKS:
        if b.get("title").casefold() == book_title.casefold():
            return b
    return "Resourse not found", 404

@app.get("/book/search/{book_author}/")
async def search_book(book_author:str, category: str | None = None):
    results = []
    category = category if category is not None and category != "" else ""
    for b in BOOKS:
        if category:
            if (b.get("category").casefold() == category.casefold()):
                results.append(b)

        if (b.get("author").casefold() == book_author.casefold()):
            results.append(b)

    return results








