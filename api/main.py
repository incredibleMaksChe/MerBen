import os
from pathlib import Path
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import logging
import traceback

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "src/data"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "api/templates"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STATIC_DIR / "css", exist_ok=True)
os.makedirs(STATIC_DIR / "images", exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

app = FastAPI(title="Mercedes W124 Price API", description="API для анализа цен на Mercedes W124", version="1.0.0")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

def load_data():
    try:
        df = pd.read_csv(DATA_DIR / "raw_data.csv")
        df['price'] = df['price'].replace('[^0-9]', '', regex=True).astype(float)
        df = df.drop_duplicates(subset=['url'])
        return df
    except Exception as e:
        logging.error(f"Ошибка загрузки данных: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка загрузки данных")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return await search_cars(
        request=request,
        min_price=0.0,
        max_price=10_000_000.0,
        sort="price",
        limit=10
    )

@app.get("/search", response_class=HTMLResponse)
async def search_cars(
    request: Request,
    min_price: float = Query(default=0.0, ge=0),
    max_price: float = Query(default=10_000_000.0, ge=0),
    sort: str = Query(default="price", regex="^(price|timestamp)$"),
    limit: int = Query(default=10, le=100)
):
    try:
        df = load_data()
        filtered = df[(df['price'] >= min_price) & (df['price'] <= max_price)]
        sorted_df = filtered.sort_values(by=sort, ascending=False)
        results = sorted_df.head(limit).to_dict("records")
        return templates.TemplateResponse("index.html", {"request": request, "cars": results, "min_price": min_price, "max_price": max_price, "sort": sort, "limit": limit})
    except Exception as e:
        logging.error(f"Ошибка обработки запроса: {traceback.format_exc()}")
        return templates.TemplateResponse("error.html", {"request": request, "error": str(e)}, status_code=400)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)