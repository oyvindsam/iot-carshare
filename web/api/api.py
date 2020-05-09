from flask import Blueprint, jsonify, request, abort
from marshmallow import ValidationError

from .models import db, Person, PersonSchema, PersonTypeSchema, BookingSchema, \
    Booking, Car, BookingStatus, CarSchema

api = Blueprint('api', __name__, url_prefix='/api/')


# TODO: standarize error handling. https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages/
@api.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


@api.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e)), 400


@api.errorhandler(409)
def conflict(e):
    return jsonify(error=str(e)), 409


# authorized
@api.route('/person/<string:username>', methods=['GET'])
def get_person(username: str):
    persons = Person.query.filter_by(username=username).first()
    if persons is None:
        return abort(404, description='Person not found')
    result = PersonSchema().dumps(persons)

    return jsonify(result), 200


# add/create user
@api.route('/person', methods=['POST'])
def add_person():
    schema = PersonSchema(exclude=['id'])
    try:
        person = schema.loads(request.get_json())
    except ValidationError:
        return abort(400, description='Invalid person data')
    if Person.query.filter_by(username=person.username).first() is not None:
        return abort(409, description='User exists')
    db.session.add(person)
    db.session.commit()
    return schema.jsonify(person), 201


# authorized
@api.route('/person/<string:username>/booking', methods=['POST'])
def add_booking(username: str):
    # bookings can't already have an id
    schema = BookingSchema(exclude=['id'])
    try:
        booking = schema.loads(request.get_json())
    except ValidationError as ve:
        return abort(400, description='Invalid booking data')  # wow generic message

    # check that references to data in db is valid
    person = Person.query.get(booking.person_id)
    car = Car.query.get(booking.car_id)
    status = BookingStatus.query.get(booking.status_id)
    if person is None or username != person.username:
        return abort(403, description='Booking under wrong person')
    if None in [person, car, status]:
        return abort(400, description='Some booking data not found in db')

    # TODO: check that person does not currently have an active booking,
    # that car is available, status is available..

    db.session.add(booking)
    db.session.commit()
    return schema.jsonify(booking), 201


# TODO: Test
# authorized!!
@api.route('/person/<string:username>/booking', methods=['GET'])
def get_bookings(username: str):
    schema = BookingSchema(many=True)
    person = Person.query.filter_by(username=username).first()
    if person is None:
        return abort(404, 'User not found')
    booking = person.booking

    return schema.jsonify(booking), 200


# authorized!!
@api.route('/person/<string:username>/booking/<int:id>', methods=['GET'])
def get_booking(username: str, id: int):
    schema = BookingSchema()
    booking = Booking.query.get(id)
    if booking is None or booking.person.username != username:
        return abort(404, description='Booking does not exist under this id/username!')

    return schema.jsonify(booking), 200


@api.route('/car', methods=['GET'])
def get_cars():
    cars = Car.query.all()
    result = CarSchema(many=True).dumps(cars)
    return jsonify(result), 200


# Admin endpoints, not neccessary for assignemnt 2.
# adding this data is allows to do manually
@api.route('/person_type', methods=['POST'])
def add_person_type():
    schema = PersonTypeSchema()
    person_type = schema.loads(request.get_json())
    db.session.add(person_type)
    db.session.commit()
    return schema.jsonify(person_type), 201


@api.route('/person', methods=['GET'])
def get_persons():
    persons = Person.query.all()
    result = PersonSchema(many=True).dump(persons)
    return jsonify(result), 200
