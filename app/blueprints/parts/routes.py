from . import parts_bp
from .schemas import part_schema, parts_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Parts
from app.models import db

@parts_bp.route('/', methods=['POST']) #route servers as the trigger for the function below.
def create_part():
    try:
        data = part_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400 #Returning the error as a response so my client can see whats wrong.
    new_part = Parts(**data) #Creating Part object
    db.session.add(new_part)
    db.session.commit()
    return part_schema.jsonify(new_part), 201 

#read Parts
@parts_bp.route('/', methods=['GET'])
def read_parts():
    parts = db.session.query(Parts).all()
    return parts_schema.jsonify(parts), 200

#read individual part
@parts_bp.route('/<int:part_id>', methods=['GET'])
def read_part(part_id):
    part = db.session.get(Parts, part_id)
    return part_schema.jsonify(part), 200

#Delete a part
@parts_bp.route('/<int:part_id>', methods=['DELETE'])
def delete_part(part_id):
    part = db.session.get(Parts, part_id)
    db.session.delete(part)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted part {part_id}"}), 200


#Update a part
@parts_bp.route('/<int:part_id>', methods=['PUT'])
def update_part(part_id):
    part = db.session.get(Parts, part_id) #Query for our part to update

    if not part: #Checking if I got a part
        return jsonify({"message": "part not found"}), 404  #if not return error message
    
    try:
        part_data = part_schema.load(request.json) #Validating updates
    except ValidationError as e:
        return jsonify({"message": e.messages}), 400
    
    for key, value in part_data.items(): #Looping over attributes and values from user data dictionary
        setattr(part, key, value) # setting Object, Attribute, Value to replace

    db.session.commit()
    return part_schema.jsonify(part), 200
