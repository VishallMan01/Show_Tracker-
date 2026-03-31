from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

shows: list[dict] = [

{
    "id": 1,
    "name": "Attack on Titan",
    "watch_status": "Watched",
    "completeness": "Complete",
    "review": "4 our of 5 stars I like the show"
},
{
    "id": 2,
    "name": "Naruto",
    "watch_status": "Watched",
    "completeness": "Complete",
    "review": "Best show of my life"
},
{
    "id": 3,
    "name": "Solo Leveling",
    "watch_status": "want to watch",
    "completeness": "On-going",
    "review": ""
},
]

@app.get("/")
@app.get("/shows")
def root(request: Request):
    return templates.TemplateResponse(
        request, 
        "home.html", 
        {"shows": shows, "name": "Home"},
    )

@app.get("/shows/{show_id}", include_in_schema=False)
def show_page(request: Request, show_id: int):
    for show in shows:
        if show.get("id") == show_id:
            title = show.get("name")
            return templates.TemplateResponse(
            request, 
            "show.html", 
            {"show": show, "name": title},
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Show was not found")


@app.get("/api/shows")
def get_shows():
    return shows

@app.get("/api/shows/{show_id}")
def get_show(show_id: int):
    for show in shows:
        if show.get("id") == show_id:
            return show
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Show was not found")


@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message},
        )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()},
        )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )