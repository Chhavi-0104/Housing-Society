from datetime import timedelta
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from werkzeug.security import generate_password_hash,check_password_hash
from fastapi.encoders import jsonable_encoder

from database import Session,engine
from schemas import SignupModel,LoginModel,UserUpdateModel
from models import User

auth_router = APIRouter()

session=Session(bind=engine)

def func(user1:LoginModel,access_token:str):
    user_to_update = session.query(User).filter(User.email==user1.email).first()
    user_to_update.token= access_token
    session.commit()

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
        users = session.query(User.id,User.username,User.email,User.admin).filter(User.is_active==1).offset(0).limit(100).all()
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
    )
    session.add(new_user)
    session.commit()
    response={
            "detail":"Registration Successfull",
            "username":user.username,
            "email":user.email
        }
    return response


@auth_router.post('/login',status_code=201)
async def login(user:LoginModel,Authorize:AuthJWT=Depends()):

    """
    ## Registered user can login using this route
    You need To Enter:
     - username : str
     - password : str
    """

    db_user=session.query(User).filter(User.email== user.email).first()
    if db_user.is_active:
        if db_user and check_password_hash(db_user.password,user.password):
            access_token=Authorize.create_access_token(subject=db_user.email,expires_time=timedelta(days=1))
            refresh_token=Authorize.create_refresh_token(subject=db_user.email,expires_time=timedelta(days=1))
            func(user,access_token)
            response={
                "message":"Login Successfull",
                "username":db_user.username,
                "email":db_user.email,
                "admin":db_user.admin,
                "access_token":access_token,
                "refresh_token":refresh_token
            }

            return jsonable_encoder(response)
    if db_user.is_active == False:
        raise HTTPException(status_code=400,detail="Account Deactivated Contact Admin")
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
    - is_active : bool
    """

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=401,detail="Invalid Token")

    current_user =Authorize.get_jwt_subject()
    user= session.query(User).filter(User.email==current_user).first()
    if user.admin:
        user_to_update = session.query(User).filter(User.id==id).first()
        user_to_update.username=user1.username
        user_to_update.email= user1.email
        user_to_update.admin= user1.admin
        user_to_update.is_active = user1.is_active
        session.commit()
        response={
            "message":"Updated successfully using admin rights",
            "username":user1.username,
            "email":user1.email,
            "is_active":user1.is_active
        }
        return response

    raise HTTPException(status_code=401,detail="You are not Admin")

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
