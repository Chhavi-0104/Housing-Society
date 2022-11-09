from datetime import timedelta
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from werkzeug.security import generate_password_hash,check_password_hash
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import load_only

from database import Session,engine
from schemas import SignupModel,LoginModel,UserUpdateModel
from models import User



auth_router = APIRouter()

session=Session(bind=engine)


def func(user1:LoginModel,access_token:str):
    user_to_update = session.query(User).filter(User.email==user1.email).first()
    user_to_update.token= access_token
    session.commit()

@auth_router.get('/welcome',status_code=200)
async def hello(Authorize:AuthJWT=Depends()):

    """
    ## Welcome Route
    This Returns Welcome Message To Authorised User
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=401,detail="Invalid Token")
    current_user =Authorize.get_jwt_subject()
    user= session.query(User).filter(User.email==current_user).first()
    if user.admin:
        return {"message":"Admin Welcome To the Society"}
    return {"message":"Welcome To the Society"}

@auth_router.get('/users',status_code=200)
async def show_users(Authorize:AuthJWT=Depends()):

    """
    ## Shows Registered users (Admin Rights required)
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=401,detail="Invalid Token")
    current_user =Authorize.get_jwt_subject()
    user= session.query(User).filter(User.email==current_user).first()
    if user.admin:
        users = session.query(User).offset(0).limit(100).all()
        return users
    raise HTTPException(status_code=401,detail="You are not Admin. Only Admins can view Registered Users")

@auth_router.post('/signup',status_code=201)
async def signup(user:SignupModel,Authorize:AuthJWT=Depends()):

    """
    ## New User can Signup
    You need To Enter:
    - username : str
    - email : str
    - password : str
    - admin : bool
    """

    db_email=session.query(User).filter(User.email ==user.email).first()
    if db_email is not None:
        return HTTPException(status_code=400,
            detail="User with Email already exists"
        )

    db_username=session.query(User).filter(User.username ==user.username).first()
    if db_username is not None:
        return HTTPException(status_code=400,
            detail="User with Username already exists"
        )

    new_user=User(
        username=user.username,
        email=user.email,
        password= generate_password_hash(user.password),
        admin =user.admin
    )
    session.add(new_user)
    session.commit()
    db_user=session.query(User).filter(User.email== user.email).first()
    access_token=Authorize.create_access_token(subject=db_user.email,expires_time=timedelta(days=1))
    func(user,access_token)
    return {"message":"Registration Successfull","access":access_token}


@auth_router.post('/login',status_code=200)
async def login(user:LoginModel,Authorize:AuthJWT=Depends()):

    """
    ## Registered user can login using this route
    You need To Enter:
     - username : str
     - password : str
    """

    db_user=session.query(User).filter(User.email== user.email).first()
    if db_user and check_password_hash(db_user.password,user.password):
        access_token=Authorize.create_access_token(subject=db_user.email,expires_time=timedelta(days=1))
        refresh_token=Authorize.create_refresh_token(subject=db_user.email,expires_time=timedelta(days=1))
        func(user,access_token)
        response={
            "message":"Login Successfull",
            "token":access_token,
            "refresh_token":refresh_token
        }

        return jsonable_encoder(response)
    raise HTTPException(status_code=400,detail="Invalid Email or Password")

@auth_router.put('/users/{id}',status_code=200)
async def update_user(id:int,user1:UserUpdateModel,Authorize:AuthJWT=Depends()):

    """
    ## Update user who is already registered (Admin Rights required)
    If you are not admin you can update only your profile
    You need To Enter:
    - username : str
    - email : str
    - admin : bool
    """

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=401,detail="Invalid Token")

    current_user =Authorize.get_jwt_subject()
    user= session.query(User).filter(User.email==current_user).first()
    if user.id==id or user.admin:
        user_to_update = session.query(User).filter(User.id==id).first()
        user_to_update.username=user1.username
        user_to_update.email= user1.email
        user_to_update.admin= user1.admin
        session.commit()
        if user.admin:
            return {"message":"Updated successfully using admin rights"}
        return {"message":"Updated successfully"}

    raise HTTPException(status_code=401,detail="You cannot modify someone else's details OR You must have admin rights")


@auth_router.delete('/users/{id}',status_code=202)
async def delete_user(id:int,Authorize:AuthJWT=Depends()):

    """
    ## This route deletes existing user
    User need to enter id (Admin Rights required)
    If you are not admin you can update only your profile
    """

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=401,detail="Invalid Token")

    current_user =Authorize.get_jwt_subject()
    user= session.query(User).filter(User.email==current_user).first()
    if user.id==id or user.admin:
        user_to_delete = session.query(User).filter(User.id==id).first()
        session.delete(user_to_delete)
        session.commit()
        if user.admin:
            return {"message":"Deleted successfully using admin rights"}
        return {"message":"Deleted successfully"}

    raise HTTPException(status_code=401,detail="You cannot delete someone else's details OR You must have admin rights")

@auth_router.get('/refresh')
async def refresh_token(Authorize:AuthJWT=Depends()):

    """
    ## Helps to refresh access_token
    """

    try:
        Authorize.jwt_refresh_token_required()
    except Exception as e:
        raise HTTPException(status_code=401,detail="Please provide valid refresh token")
    
    current_user=Authorize.get_jwt_subject()
    access_token =Authorize.create_access_token(subject=current_user)
    return jsonable_encoder({"access":access_token})