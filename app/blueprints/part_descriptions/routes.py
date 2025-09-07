from . import part_descriptions_bp
from .schemas import part_description_schema, part_descriptions_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Part_descriptions
from app.models import db

@part_descriptions_bp.route('/', methods=['POST']) #route servers as the trigger for the function below.
def create_part_description():
    try:
        data = part_description_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400 #Returning the error as a response so my client can see whats wrong.
    
    new_part_description = Part_descriptions(**data) #Creating User object
    db.session.add(new_part_description)
    db.session.commit()
    return part_description_schema.jsonify(new_part_description), 201 

#read Part_descriptions
@part_descriptions_bp.route('/', methods=['GET'])
def read_part_descriptions():
    part_descriptions = db.session.query(Part_descriptions).all()
    return part_descriptions_schema.jsonify(part_descriptions), 200

#read individual part_description
@part_descriptions_bp.route('/<int:part_description_id>', methods=['GET'])
def read_part_description(part_description_id):
    part_description = db.session.get(Part_descriptions, part_description_id)
    return part_description_schema.jsonify(part_description), 200

#Delete a part_description
@part_descriptions_bp.route('/<int:part_description_id>', methods=['DELETE'])
def delete_part_description(part_description_id):
    part_description = db.session.get(Part_descriptions, part_description_id)
    db.session.delete(part_description)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted part_description {part_description_id}"}), 200


#Update a part_description
@part_descriptions_bp.route('/<int:part_description_id>', methods=['PUT'])
def update_part_description(part_description_id):
    part_description = db.session.get(Part_descriptions, part_description_id) #Query for our part_description to update

    if not part_description: #Checking if I got a part_description
        return jsonify({"message": "part_description not found"}), 404  #if not return error message
    
    try:
        part_description_data = part_description_schema.load(request.json) #Validating updates
    except ValidationError as e:
        return jsonify({"message": e.messages}), 400
    
    for key, value in part_description_data.items(): #Looping over attributes and values from user data dictionary
        setattr(part_description, key, value) # setting Object, Attribute, Value to replace

    db.session.commit()
    return part_description_schema.jsonify(part_description), 200
