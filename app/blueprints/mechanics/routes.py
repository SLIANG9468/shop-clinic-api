from . import mechanics_bp
from .schemas import mechanic_schema, mechanics_schema, login_schema
from app.blueprints.service_tickets.schemas import service_ticket_schema, service_tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Mechanics
from app.models import db
from werkzeug.security import generate_password_hash, check_password_hash
from app.util.auth import encode_token, token_required
from sqlalchemy.exc import IntegrityError

@mechanics_bp.route('/login', methods=['POST'])

def login():
    try:
        data = login_schema.load(request.json) # Send email and password
    except ValidationError as e:
        return jsonify(e.messages), 400 #Returning the error as a response so my client can see whats wrong.
    
    mechanic = db.session.query(Mechanics).where(Mechanics.email==data['email']).first() #Search my db for a mechanic with the passed in email

    if mechanic and check_password_hash(mechanic.password, data['password']): #Check the mechanic stored password hash against the password that was sent
        token = encode_token(mechanic.id, role='mechanic')
        return jsonify({
            "message": f'Welcome {mechanic.last_name}',
            "token": token,
            "mechanic":mechanic_schema.dump(mechanic)
        }), 200
    
    return jsonify("Invalid email or password!"), 403


@mechanics_bp.route('/', methods=['POST']) #route servers as the trigger for the function below.
def create_mechanic():
    try:
        data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400 #Returning the error as a response so my client can see whats wrong.
    
    data['password'] = generate_password_hash(data['password'])
    new_mechanic = Mechanics(**data) #Creating User object
    try:
        db.session.add(new_mechanic)
        db.session.commit()
        return mechanic_schema.jsonify(new_mechanic), 201 
    except IntegrityError as e:
        db.session.rollback()
        return jsonify("email already exists"),400

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
@token_required
def delete_mechanic(mechanic_id):
    token_id = request.mechanic_id
    mechanic = db.session.get(Mechanics, token_id)
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
    
    for key, value in mechanic_data.items(): #Looping over attributes and values from mechanic data dictionary
        setattr(mechanic, key, value) # setting Object, Attribute, Value to replace

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

#get my tickets
@mechanics_bp.route('/my-tickets/<int:mechanic_id>', methods = ['GET'])
@token_required
def get_my_tickets(mechanic_id):
    token_id = request.mechanic_id
    mechanic = db.session.get(Mechanics, token_id)
    
    if not mechanic:
        return jsonify({"message": "mechanic not found"}), 404

    return service_tickets_schema.jsonify(mechanic.service_tickets), 200

# mechanic who has worked on the most ticket
@mechanics_bp.route('/most-tickets/', methods = ['GET'])
def get_mechanics_worked_most_tickets():
    print(" in the right route")
    mechanics = db.session.query(Mechanics).all()
    print(f"all mechanics: {mechanics}")

    mechanics.sort(key= lambda mechanic: len(mechanic.service_tickets), reverse = True)
    output = []
    for mechanic in mechanics:
        print(f"mechanic id: {mechanic.id}")
        mechanic_format = {
            "mechanic": mechanic_schema.dump(mechanic),
            "service_tickets": len(mechanic.service_tickets)
        }
        output.append(mechanic_format)
    return jsonify(output), 200
