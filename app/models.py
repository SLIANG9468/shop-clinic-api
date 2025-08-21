from datetime import date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Date, ForeignKey, String, Table, Column, Float



#Create a base class for our models
class Base(DeclarativeBase):
    pass
    #could add your own config


#Instatiate your SQLAlchemy database:

db = SQLAlchemy(model_class = Base)



ticket_mechanics = Table(
    'ticket_mechanics',
    Base.metadata,
    Column('ticket_id', ForeignKey('service_tickets.id')),
    Column('mechanic_id', ForeignKey('mechanics.id'))
)

class Customers(Base):
    __tablename__ = 'customers' #lowercase plural form of resource

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(360), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=True)

    #One to Many relationship from customer to service_tickets
    service_tickets: Mapped[list['Service_tickets']] = relationship('Service_tickets', back_populates = 'customer')

class Mechanics(Base):
    __tablename__ = 'mechanics' #lowercase plural form of resource

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(120), nullable = False)
    last_name: Mapped[str] = mapped_column(String(120), nullable = False)
    email: Mapped[str] = mapped_column(String(360), unique=True, nullable = False)
    password: Mapped[str] = mapped_column(String(20), nullable = False)
    salary: Mapped[float] = mapped_column(Float, nullable = False)
    address: Mapped[str] = mapped_column(String(500), nullable=True)

    service_tickets: Mapped[list['Service_tickets']] = relationship('Service_tickets', secondary= ticket_mechanics,back_populates='mechanics')

class Service_tickets(Base):
    __tablename__ = 'service_tickets'

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'), nullable=False)
    service_desc: Mapped[str] = mapped_column(String(120), nullable=False)
    price: Mapped[float] = mapped_column(Float)
    VIN: Mapped[str] = mapped_column(String(30), nullable=False)
    loan_date: Mapped[date] = mapped_column(Date, nullable=True)
    service_date: Mapped[date] = mapped_column(Date, nullable=True)

    #Relationships
    customer: Mapped['Customers'] = relationship('Customers', back_populates='service_tickets')
    mechanics: Mapped[list['Mechanics']] = relationship("Mechanics", secondary=ticket_mechanics, back_populates='service_tickets') #Many to Many relationship going through the loan_books table
   