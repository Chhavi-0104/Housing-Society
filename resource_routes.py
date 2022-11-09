from fastapi import APIRouter,Depends
from fastapi_jwt_auth import AuthJWT
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder

from database import Session,engine
from models import Resource,User
from schemas import  ResModel

resource_router = APIRouter()
session=Session(bind=engine)

@resource_router.post('/resources',status_code=201)
async def add_resource(add:ResModel,Authorize:AuthJWT=Depends()):

    """
    ## Adding a Resource (Admin Rights required)
    You need To Enter:
    - resource_name : str
    - amount : int
    - availability : str
    """

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=401,detail="Invalid Token")
    current_user =Authorize.get_jwt_subject()
    user=session.query(User).filter(User.email==current_user).first()
    if user.admin:
        new_Resource=Resource(
            resource_name=add.resource_name,
            availability=add.availability,
            amount= add.amount
        )
        new_Resource.user=user
        session.add(new_Resource)
        session.commit()
        response={
            "resource_name":new_Resource.resource_name,
            "availability": new_Resource.availability,
            "amount" : new_Resource.amount,
            "id": new_Resource.id
        }
        return {"message":"Resource added Successfully"}
    raise HTTPException(status_code=401,detail="You are not Admin")

@resource_router.get('/resources',status_code=200)
async def list_all_resources(Authorize:AuthJWT=Depends()):
    """
    ## View Resources
    Shows Resource_name,Availability and id
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=401,detail="Invalid Token")
    res=session.query(Resource).all()
    return jsonable_encoder(res)

@resource_router.put('/resources/{id}',status_code=200)
async def update_resource(id:int,res1:ResModel,Authorize:AuthJWT=Depends()):
    """
    ## Updating a Resource (Admin Rights required)
    You need To Enter:
    - resource_name : str
    - amount : int
    - availability : str 
    """

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=401,detail="Invalid Token")
    current_user =Authorize.get_jwt_subject()
    user=session.query(User).filter(User.email==current_user).first()
    if user.admin:   
        res_to_update = session.query(Resource).filter(Resource.id==id).first()
        res_to_update.resource_name=res1.resource_name
        res_to_update.amount=res1.amount
        res_to_update.availability= res1.availability
        session.commit()
        return {"message":"Resource Updated Succesfully"}
    raise HTTPException(status_code=401,detail="You are not Admin")

@resource_router.delete('/resources/{id}',status_code=200)
async def delete_res(id:int,Authorize:AuthJWT=Depends()):
    """
    ## Deleting a Resource (Admin Rights required)
    You need To Enter:
    - resource id : int
    """

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=401,detail="Invalid Token")
    current_user =Authorize.get_jwt_subject()
    user=session.query(User).filter(User.email==current_user).first()
    if user.admin:  
        res_to_delete = session.query(Resource).filter(Resource.id==id).first()
        session.delete(res_to_delete)
        session.commit()
        return {"message":"Resource deleted Succesfully"}
    raise HTTPException(status_code=401,detail="You are not Admin")
