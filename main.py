from pathlib import Path
from fastapi import FastAPI, Request, status
from .models import Base
from .database import engine
from .dependencies import NotAuthenticated
from .routers import auth, todos, admin, users, pages
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app = FastAPI()

Base.metadata.create_all(bind=engine)


BASE_DIR = Path(__file__).resolve().parent

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.exception_handler(NotAuthenticated)
async def redirect_to_login(request: Request, exc: NotAuthenticated):
    response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    return response


@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}


app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
