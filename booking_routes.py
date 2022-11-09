from fastapi import APIRouter,Depends
from fastapi_jwt_auth import AuthJWT
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder

from models import Booking,User,Resource
from schemas import BookingAdd
from database import Session,engine

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
    user=session.query(User).filter(User.email==current_user).first()
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
                "status" : new_booking.status
            }
            return response
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
    user=session.query(User).filter(User.email==current_user).first()
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
    user= session.query(User).filter(User.email==current_user).first()
    if user.admin:
        booking=session.query(Booking.id,Booking.resource_name,Booking.Date_Booked,Booking.status).filter(Booking.id==id).first()
        test=session.query(Booking.user_id,Booking.res_id).filter(Booking.id==id).first()
        us=session.query(User.username,User.email).filter(User.id==test.user_id).first()
        res_info=session.query(Resource.resource_name,Resource.amount).filter(Resource.id==test.res_id).first()
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
    user= session.query(User).filter(User.email==current_user).first()
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
    user= session.query(User).filter(User.email==current_user).first()
    res=session.query(Resource).filter(Resource.resource_name==book.resource_name).first()
    if user.admin:
        if res.availability=="Available":
            booking_to_update = session.query(Booking).filter(Booking.id==id).first()
            booking_to_update.resource_name= book.resource_name
            booking_to_update.Date_Booked= book.Date_Booked
            booking_to_update.status=book.status
            booking_to_update.res=res
            session.commit()
            return {"message":"Booking Updated Successfully"}
        elif res.availability=="Not Available":
                raise HTTPException(status_code=401,detail="Sorry Resource Not Available")
            
    raise HTTPException(status_code=401,detail="You are not Admin")

