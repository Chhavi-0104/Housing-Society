from fastapi import APIRouter,Depends
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import delete
from models import Booking,User,Resource
from schemas import BookingAdd
from fastapi.exceptions import HTTPException
from database import Session,engine
from fastapi.encoders import jsonable_encoder


booking_router = APIRouter()
session=Session(bind=engine)

@booking_router.post('/bookings',status_code=201)
async def add_booking(book:BookingAdd,Authorize:AuthJWT=Depends()):
    """
    ##Book Resources here
    You need To Enter:   
    - resource_name : str
    - Date_Booked : date
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=401,detail="Invalid Token")
    current_user =Authorize.get_jwt_subject()
    user=session.query(User).filter(User.username==current_user).first()
    res=session.query(Resource).filter(Resource.resource_name==book.resource_name).first()
    if res.availability == "Available" :
        try:
            new_booking=Booking(
                resource_name = book.resource_name,
                Date_Booked=book.Date_Booked
            )
            new_booking.user=user
            new_booking.res=res
            session.add(new_booking)
            session.commit()
            response={
                "resource_name":new_booking.resource_name,
                "Date_Booked":new_booking.Date_Booked,
                "id": new_booking.id,
            }
            return {"message":"Booking Successfull"}
        except Exception as e:
            raise HTTPException(status_code=500,detail="This resource already booked on this date.")
    return {"message":"Sorry Resource Not Available"}

@booking_router.get('/bookings',status_code=200)
async def list_all_bookings(Authorize:AuthJWT=Depends()):
    """
    ##Check all bookings (Admin Rights Required)
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=401,detail="Invalid Token")
    current_user =Authorize.get_jwt_subject()
    user=session.query(User).filter(User.username==current_user).first()
    if user.admin:
        bookings=session.query(Booking).all()
        return jsonable_encoder(bookings)
    
    raise HTTPException(status_code=401,detail="You are not Admin")

@booking_router.get('/bookings/{id}',status_code=200)
async def get_booking_by_id(id:int,Authorize:AuthJWT=Depends()):
    """
    ##Check bookings by particular id (Admin Rights Required)
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=401,detail="Invalid Token")
    current_user =Authorize.get_jwt_subject()
    user= session.query(User).filter(User.username==current_user).first()
    if user.admin:
        booking=session.query(Booking).filter(Booking.id==id).first()
        us=session.query(User).filter(User.id==booking.user_id).first()
        res_info=session.query(Resource).filter(Resource.id==booking.res_id).first()
        result={ "booking": booking,"user":us,"resource_info": res_info}
        return jsonable_encoder(result)

    raise HTTPException(status_code=401,detail="You are not Admin")
    
@booking_router.get('/user_bookings',status_code=200)
async def get_user_booking(Authorize:AuthJWT=Depends()):
    """
    ##Check all bookings of current user
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=401,detail="Invalid Token")
    current_user =Authorize.get_jwt_subject()
    user= session.query(User).filter(User.username==current_user).first()
    return jsonable_encoder(user.bookings)

@booking_router.put('/bookings/{id}',status_code=200)
async def update_user_booking(id:int,book:BookingAdd,Authorize:AuthJWT=Depends()):
    """
    ##Check all bookings (Admin Rights Required)
    You need To Enter:
    - resource_name : str
    - Date_Booked : date
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=401,detail="Invalid Token")
    current_user =Authorize.get_jwt_subject()
    user= session.query(User).filter(User.username==current_user).first()
    if user.admin:
        booking_to_update = session.query(Booking).filter(Booking.id==id).first()
        booking_to_update.resource_name= book.resource_name
        booking_to_update.Date_Booked= book.Date_Booked
        session.commit()
        return {"message":"Booking Updated Successfully"}
    raise HTTPException(status_code=401,detail="You are not Admin")

@booking_router.delete('/bookings/{id}',status_code=200)
async def delete_user_booking(id:int,Authorize:AuthJWT=Depends()):
    """
    ##Delete Booking by id (Admin Rights Required)
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=401,detail="Invalid Token")
    current_user =Authorize.get_jwt_subject()
    user= session.query(User).filter(User.username==current_user).first()
    if user.admin:
        booking_to_delete = session.query(Booking).filter(Booking.id==id).first()
        session.delete(booking_to_delete)
        session.commit()
        return {"message":"Booking Removed Successfully"}
    raise HTTPException(status_code=401,detail="You are not Admin")

