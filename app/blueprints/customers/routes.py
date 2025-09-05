from . import customers_bp
from .schemas import customer_schema, customers_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Customers
from app.models import db
from app.extensions import limiter, cache

@customers_bp.route('/', methods=['POST']) #route servers as the trigger for the function below.
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
@customers_bp.route('/', methods=['GET'])
@cache.cached(timeout = 30)
def read_customers():
    customers = db.session.query(Customers).all()
    return customers_schema.jsonify(customers), 200

#read individual customer
@customers_bp.route('/<int:customer_id>', methods=['GET'])
def read_customer(customer_id):
    customer = db.session.get(Customers, customer_id)
    return customer_schema.jsonify(customer), 200

#Delete a customer
@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
@limiter.limit("5 per day")
def delete_customer(customer_id):
    customer = db.session.get(Customers, customer_id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted customer {customer_id}"}), 200


#Update a customer
@customers_bp.route('/<int:customer_id>', methods=['PUT'])
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
