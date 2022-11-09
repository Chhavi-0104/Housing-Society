from fastapi import FastAPI

from auth_routes import auth_router 
from resource_routes import resource_router
from booking_routes import booking_router
from fastapi_jwt_auth import AuthJWT
from schemas import Settings
from database import engine
import models
from fastapi.middleware.cors import CORSMiddleware


models.Base.metadata.create_all(bind=engine)

app=FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@AuthJWT.load_config
def get_config():
    return Settings()

app.include_router(auth_router)
app.include_router(resource_router)
app.include_router(booking_router)
 #chhavi
