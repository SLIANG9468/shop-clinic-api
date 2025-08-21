from datetime import date
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Date, ForeignKey, String, Table, Column, Float
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError

app = Flask(__name__) #Instatiating our Flask app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db' #Connecting a sqlite db to our flask app


#Create a base class for our models
class Base(DeclarativeBase):
    pass
    #could add your own config


#Instatiate your SQLAlchemy database:

db = SQLAlchemy(model_class = Base)
ma = Marshmallow()

#Initialize my extension onto my Flask app

db.init_app(app) #adding the db to the app.
ma.init_app(app)

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
   
#Install Marshmellow
#pip install flask-marshmallow marshmallow-sqlalchemy

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customers #Creates a schema that validates the data as defined by our Customers Model

customer_schema = CustomerSchema() #Creating an instance of my schema that I can actually use to validate, deserialize, and serialze JSON


#=========================================== CRUD for Customers =========================================

@app.route('/customers', methods=['POST']) #route servers as the trigger for the function below.
def create_customer():
    try:
        data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400 #Returning the error as a response so my client can see whats wrong.
    
    new_customer = Customers(**data) #Creating User object
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201 

#read Customers
@app.route('/customers', methods=['GET'])
def read_customers():
    customers = db.session.query(Customers).all()
    return customer_schema.jsonify(customers, many=True), 200

#read individual customer
@app.route('/customers/<int:customer_id>', methods=['GET'])
def read_customer(customer_id):
    customer = db.session.get(Customers, customer_id)
    return customer_schema.jsonify(customer), 200

#Delete a customer
@app.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    customer = db.session.get(Customers, customer_id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted customer {customer_id}"}), 200


#Update a customer
@app.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    customer = db.session.get(Customers, customer_id) #Query for our customer to update

    if not customer: #Checking if I got a customer
        return jsonify({"message": "customer not found"}), 404  #if not return error message
    
    try:
        customer_data = customer_schema.load(request.json) #Validating updates
    except ValidationError as e:
        return jsonify({"message": e.messages}), 400
    
    for key, value in customer_data.items(): #Looping over attributes and values from user data dictionary
        setattr(customer, key, value) # setting Object, Attribute, Value to replace

    db.session.commit()
    return customer_schema.jsonify(customer), 200

with app.app_context():
    db.create_all() #Creating our database tables


app.run(debug=True)