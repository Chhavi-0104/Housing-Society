from sqlalchemy import Boolean, Column, Integer, String,Text,ForeignKey,UniqueConstraint
from sqlalchemy.types import Date
from sqlalchemy.orm import relationship


from database import Base

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True)
    email=Column(String(80),unique=True)
    password = Column(Text, nullable=True)
    admin= Column(Boolean,default=False)
    token=Column(String)
    is_active=Column(Boolean,default=True)
    bookings=relationship('Booking',back_populates='user')

    def __repr__(self):
        return f"<User {self.username}>"

class Booking(Base):
    __tablename__ = "booking"
  
    id = Column(Integer, primary_key=True)
    resource_name = Column(String(25))
    user_id =Column(Integer,ForeignKey('user.id'))
    res_id=Column(Integer,ForeignKey('resource.id'))
    Date_Booked=Column(Date)
    status = Column(String(25),default="Successfull")
    user=relationship('User',back_populates='bookings')
    res=relationship('Resource',back_populates='resources')
    __table_args__ = (UniqueConstraint('res_id', 'Date_Booked', name='combo'),)

    def __repr__(self):
        return f"<Booking {self.id}>"

class Resource(Base):
    __tablename__ = "resource"
  
    id = Column(Integer, primary_key=True)
    resource_name = Column(String(25), unique=True)
    availability= Column(String(20),default="Available")
    amount= Column(Integer)
    resources=relationship('Booking',back_populates='res')

    def __repr__(self):
        return f"<Resource {self.id}>"
