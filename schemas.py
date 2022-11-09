from pydantic import BaseModel
from typing import Optional
from datetime import date

class SignupModel(BaseModel):
    id :Optional[int]
    username : str
    email: str
    password :str

    class Config:
        arbitrary_types_allowed = True
        orm_mode=True
        schema_extra={
            'example':{
                "username":"John",
                "email":"john@gmail.com",
                "password":"john123",
            }
        }

class UserUpdateModel(BaseModel):
    id :Optional[int]
    username :Optional[str]
    email: Optional[str]
    admin: Optional[bool]
    is_active:Optional[bool]
    class Config:
        arbitrary_types_allowed = True
        orm_mode=True
        schema_extra={
            'example':{
                "username":"John",
                "email":"john@gmail.com",
                "admin":"False",
                "is_active":"True"
            }
        }

class  Settings(BaseModel):
    authjwt_secret_key:str='ea89de0d23fa63864faa983dd60c616769f5b165c255e8fe9593d845e2891cec'

class LoginModel(BaseModel):
    email:str
    password:str

class ResModel(BaseModel):
    id : Optional[int]
    resource_name :str
    amount:int
    availability: Optional[str] 
    class Config:
        orm_mode=True
        schema_extra={
            "example":{
                "resource_name":"Hall",
                "amount":"2000"
            }
        }

class BookingAdd(BaseModel):
    id : Optional[int]
    resource_name: str
    user_id :Optional[int]
    Date_Booked: date
    status:Optional[str]
    class Config:
        orm_mode = True
        schema_extra={
            "example":{
                "resource_name":"Hall",
                "Date_Booked":"2013-01-14T00:00:00Z"
            }
        }
