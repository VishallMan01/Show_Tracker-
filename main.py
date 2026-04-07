from typing import Annotated

from fastapi import FastAPI, Request, HTTPException, status, Depends 
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

import models
from database import Base, engine, get_db
from schema import ShowCreate, ShowResponse, UserCreate, UserResponse

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

templates = Jinja2Templates(directory="templates")


@app.get("/", include_in_schema=False)
@app.get("/shows", include_in_schema=False)
def root(request: Request, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Show))
    shows = result.scalars().all()
    return templates.TemplateResponse(
        request, 
        "home.html", 
        {"shows": shows, "name": "Home"},
    )


@app.get("/shows/{show_id}", include_in_schema=False)
def show_page(request: Request, show_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Show).where(models.Show.id == show_id))
    show = result.scalars().first()
    if show:
        title = show.name
        return templates.TemplateResponse(
            request, 
            "show.html", 
            {"show": show, "name": title},
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Show was not found")


@app.get("/users/{user_id}/shows", include_in_schema=False, name="user_shows") 
def user_post_page(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") 
    
    result = db.execute(select(models.Show).where(models.Show.user_id == user_id))
    shows = result.scalars().all()
    return templates.TemplateResponse(
        request, 
        "user_shows.html", 
        {"shows": shows, "user": user, "name": f"{user.username}'s Shows"},
    )


@app.post("/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.username == user.username))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists")
    
    result = db.execute(select(models.User).where(models.User.email == user.email))
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists")
    
    new_user = models.User(
        username=user.username,
        email=user.email,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@app.get("/api/users/{user_id}/shows", response_model=list[ShowResponse])
def get_user_shows(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Show).where(models.Show.user_id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") 
    
    result = db.execute(select(models.Show).where(models.Show.user_id == user_id))
    shows = result.scalars().all()
    return shows


@app.get("/api/shows", response_model=list[ShowResponse])
def get_shows(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Show))
    shows = result.scalars().all()
    return shows


@app.post("/api/shows", response_model=ShowResponse, status_code=status.HTTP_201_CREATED)
def create_show(show: ShowCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == show.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    new_show = models.Show(
        name=show.name,
        watch_status=show.watch_status,
        completeness=show.completeness,
        review=show.review,
        user_id=show.user_id,
    )
    db.add(new_show)
    db.commit()
    db.refresh(new_show)
    return new_show


@app.get("/api/shows/{show_id}", response_model=ShowResponse)
def get_show(show_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Show).where(models.Show.id == show_id))
    show = result.scalars().first()
    if not show:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Show not found")
    return show


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