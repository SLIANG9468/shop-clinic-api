from . import service_tickets_bp
from .schemas import service_ticket_schema, service_tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Service_tickets, db, Mechanics
from app.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema

from datetime import datetime, date

#CREATE SERVICE_TICKET
@service_tickets_bp.route('', methods=['POST'])
def create_service_ticket():
    try:
        data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_service_ticket = Service_tickets(**data)
    db.session.add(new_service_ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(new_service_ticket) #use jsonify when the schema is return the whole message


#Assign mechanic to service_ticket
@service_tickets_bp.route('/<int:service_ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])

def add_mechanic(service_ticket_id, mechanic_id):
    service_ticket = db.session.get(Service_tickets, service_ticket_id)
    mechanic = db.session.get(Mechanics, mechanic_id)

    if mechanic not in service_ticket.mechanics: #checking to see if a relationship already exist between service_ticket and mechanic
        service_ticket.mechanics.append(mechanic) #creating a relationship between service_ticket and mechanic
        db.session.commit()
        return jsonify({
            'message': f'successfully add {mechanic.last_name} to service_ticket',
            'service_ticket': service_ticket_schema.dump(service_ticket),  #use dump when the schema is adding just a piece of the return message
            'mechanics': mechanics_schema.dump(service_ticket.mechanics) #using the mechanics_schema to serialize the list of mechanics related to the service_ticket
        }), 200
    
    return jsonify("This mechanic is already on the service_ticket"), 400

#Remove mechanic from service_ticket
@service_tickets_bp.route('/<int:service_ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])

def remove_mechanic(service_ticket_id, mechanic_id):
    service_ticket = db.session.get(Service_tickets, service_ticket_id)
    mechanic = db.session.get(Mechanics, mechanic_id)

    if mechanic in service_ticket.mechanics: #checking to see if a relationship already exist between service_ticket and mechanic
        service_ticket.mechanics.remove(mechanic) #removing the relationship between service_ticket and mechanic
        db.session.commit()
        return jsonify({
            'message': f'successfully removed {mechanic.last_name} from service_ticket',
            'service_ticket': service_ticket_schema.dump(service_ticket),  #use dump when the schema is adding just a piece of the return message
            'mechanics': mechanics_schema.dump(service_ticket.mechanics) #using the mechanics_schema to serialize the list of mechanics related to the service_ticket
        }), 200
    
    return jsonify("This mechanic is no on the service_ticket"), 400


@service_tickets_bp.route('', methods=['GET'])
def get_service_tickets():
    service_tickets = db.session.query(Service_tickets).all()
    return service_tickets_schema.jsonify(service_tickets), 200
