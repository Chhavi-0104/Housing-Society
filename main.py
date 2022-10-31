from fastapi import FastAPI

from auth_routes import auth_router 
from book_routes import book_router
from booking_routes import booking_router
from fastapi_jwt_auth import AuthJWT
from schemas import Settings
from database import engine
import models


models.Base.metadata.create_all(bind=engine)

app=FastAPI()

@AuthJWT.load_config
def get_config():
    return Settings()

app.include_router(auth_router)
app.include_router(book_router)
app.include_router(booking_router)
