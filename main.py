from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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
    "id": 2,
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

@app.get("/api/shows")
def get_shows():
    return shows