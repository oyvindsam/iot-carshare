from flask import Blueprint, jsonify, request, abort
from flask_marshmallow import Schema
from marshmallow import ValidationError

from .models import db, Person, PersonSchema, PersonTypeSchema, BookingSchema, \
    Booking

api = Blueprint('api', __name__, url_prefix='/api/')

# TODO: standarize error handling. https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages/
@api.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

@api.route('/person', methods=['GET'])
def get_persons():
    persons = Person.query.all()
    result = PersonSchema(many=True).dump(persons)

    return jsonify(result), 200


@api.route('/person/<string:username>', methods=['GET'])
def get_person(username: str):
    persons = Person.query.filter_by(username=username).first()
    if persons is None:
        return abort(404, description='Person not found')
    result = PersonSchema().dumps(persons)

    return jsonify(result), 200


# TODO: update person option? (id already exists in db) -> needs to be authorized
@api.route('/person', methods=['POST'])
def add_person():
    # should client ever know id?
    #schema = PersonSchema(exclude=['id'])
    schema = PersonSchema()
    data = request.get_json()
    try:
        person = schema.loads(data)
    except ValidationError:
        return jsonify(data), 400
    if person.id is not None:
        return jsonify(data), abort(409)  # db adds id
    if Person.query.filter_by(username=person.username).first() is not None:
        return jsonify(data), 404
    db.session.add(person)
    db.session.commit()
    return schema.jsonify(person), 201


@api.route('/person_type', methods=['POST'])
def add_person_type():
    schema = PersonTypeSchema()
    person_type = schema.loads(request.get_json())
    db.session.add(person_type)
    db.session.commit()
    return schema.jsonify(person_type), 201


# needs to be authorized!!
@api.route('/person/<string:username>/booking', methods=['POST'])
def add_booking(username: str):
    print("here")
    req = request
    schema = BookingSchema(exclude=['id'])
    data = request.get_json()
    try:
        booking = schema.loads(request.get_json())
    except ValidationError as ve:
        return abort(400, description='Invalid booking data')  # wow generic message
    if booking.id is not None:
        return abort(409)
    booking_person = Person.query.get(booking.person_id)
    if username != booking_person.username:
        return abort(403, description='Booking under wrong person')
    db.session.add(booking)
    db.session.commit()
    return schema.jsonify(booking), 201

# needs to be authorized!!
@api.route('/person/<string:username>/booking/<int:id>', methods=['GET'])
def get_booking(username: str):
    schema = BookingSchema()
    booking = Booking.query.get(id)
    if booking is None or booking.person.username != username:
        return abort(404, description='Booking does not exist under this id/username!')

    return schema.jsonify(booking), 200

