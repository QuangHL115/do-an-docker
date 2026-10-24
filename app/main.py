import os
import pymysql
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
templates = Jinja2Templates(directory="templates")

def get_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "db"),
        user=os.getenv("MYSQL_USER", "news_app_user"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "news_db"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM articles ORDER BY created_at DESC")
        articles = cursor.fetchall()
        cursor.execute("SELECT * FROM categories")
        categories = cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("index.html", {"request": request, "articles": articles, "categories": categories})

@app.post("/admin/create")
def create_article(title: str = Form(...), summary: str = Form(...), content: str = Form(...), category_id: int = Form(...), token: str = Form(...)):
    if token != os.getenv("ADMIN_SECRET_TOKEN", "admin123"):
        raise HTTPException(status_code=403, detail="Sai mã Admin!")
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO articles (title, summary, content, category_id) VALUES (%s, %s, %s, %s)", (title, summary, content, category_id))
        conn.commit()
    conn.close()
    return RedirectResponse(url="/", status_code=303)
