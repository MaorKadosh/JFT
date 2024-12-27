from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Sources configuration
sources = {
    "hebrew": {
        "url": "https://www.naisrael.org.il/just-for-today/",
        "start_selector": "div#JFTmain",
        "exclude_selectors": ["style", "script", "noscript", "iframe"],
        "encoding": "utf-8"
    },
    "russian": {
        "url": "https://na-russia.org/",
        "start_selector": "table",
        "exclude_selectors": ["style", "script"],
        "encoding": "utf-8"
    },
    "english": {
        "url": "https://www.jftna.org/jft/",
        "start_selector": "table",
        "exclude_selectors": ["style", "script"],
        "encoding": "utf-8"
    }
}

def fetch_content(language: str):
    """Fetch and process content for a specific language."""
    source = sources.get(language)
    if not source:
        return f"Language {language} not supported."

    try:
        response = requests.get(source["url"], timeout=10)
        response.encoding = source.get("encoding", "utf-8")  # Set the encoding
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        content_div = soup.select_one(source["start_selector"])

        if not content_div:
            return "Content not found."

        # Remove unwanted elements
        for exclude in source["exclude_selectors"]:
            for tag in content_div.select(exclude):
                tag.decompose()

        # Return raw HTML content to preserve formatting
        return str(content_div)

    except requests.exceptions.RequestException as e:
        return f"Error fetching content for {language}: {e}"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page."""
    hebrew_text = fetch_content("hebrew")
    english_text = fetch_content("english")
    russian_text = fetch_content("russian")
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "hebrew_text": hebrew_text,
            "english_text": english_text,
            "russian_text": russian_text,
        },
    )
