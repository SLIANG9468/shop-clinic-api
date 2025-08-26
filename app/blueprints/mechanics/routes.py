from . import mechanics_bp
from .schemas import mechanic_schema, mechanics_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Mechanics
from app.models import db

@mechanics_bp.route('/', methods=['POST']) #route servers as the trigger for the function below.
def create_mechanic():
    try:
        data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400 #Returning the error as a response so my client can see whats wrong.
    
    new_mechanic = Mechanics(**data) #Creating User object
    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201 

#read Mechanics
@mechanics_bp.route('/', methods=['GET'])
def read_mechanics():
    mechanics = db.session.query(Mechanics).all()
    return mechanics_schema.jsonify(mechanics), 200

#read individual mechanic
@mechanics_bp.route('/<int:mechanic_id>', methods=['GET'])
def read_mechanic(mechanic_id):
    print
    mechanic = db.session.get(Mechanics, mechanic_id)
    return mechanic_schema.jsonify(mechanic), 200

#Delete a mechanic
@mechanics_bp.route('/<int:mechanic_id>', methods=['DELETE'])
def delete_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanics, mechanic_id)
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted mechanic {mechanic_id}"}), 200


#Update a mechanic
@mechanics_bp.route('/<int:mechanic_id>', methods=['PUT'])
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanics, mechanic_id) #Query for our mechanic to update

    if not mechanic: #Checking if I got a mechanic
        return jsonify({"message": "mechanic not found"}), 404  #if not return error message
    
    try:
        mechanic_data = mechanic_schema.load(request.json) #Validating updates
    except ValidationError as e:
        return jsonify({"message": e.messages}), 400
    
    for key, value in mechanic_data.items(): #Looping over attributes and values from user data dictionary
        setattr(mechanic, key, value) # setting Object, Attribute, Value to replace

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200
