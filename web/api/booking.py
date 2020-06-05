from flask import jsonify, request, abort
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError

from api import api_blueprint, jwt
from .models import db, Person, PersonSchema, BookingSchema, \
    Booking, Car, CarSchema, BookingStatusEnum, PersonType


# Helper method to see if username (in url path) matches username from jwt,
# in case jwt_user is a customer
def is_valid_user(username, jwt_username):
    jwt_person = Person.query.filter_by(username=jwt_username).first()
    # check if user making request is customer, and if same as path user
    if jwt_person.person_type == PersonType.CUSTOMER:
        # this case happens if a customer tries to access another customer
        if jwt_username != username:
            return False
    return True


@api_blueprint.route('/person/<string:username>/booking', methods=['GET'])
@jwt_required
def get_bookings(username: str):
    """
    Get all bookings for this user

    Args:
        username (str): logged in user

    Returns: All bookings for user with additional info as json list string, example:

    """
    if not is_valid_user(username, get_jwt_identity()):
        return abort(403, description='Identity does not match url path')

    schema = BookingSchema()
    person = Person.query.filter_by(username=username).first()
    if person is None:
        return abort(404, 'User not found')
    bookings = person.booking

    person_schema = PersonSchema()
    car_schema = CarSchema()

    # TODO: add car type, color
    data = [{
        'booking': schema.dumps(booking),
        'person': person_schema.dumps(booking.person),
        'car': car_schema.dumps(booking.car)
    }
        for booking in bookings]

    return jsonify(data), 200


@api_blueprint.route('/person/<string:username>/booking', methods=['POST'])
@jwt_required
def add_booking(username: str):
    """
    Add a new booking for this user
    Args:
        username (str): logged in user

    Returns: Json string of booking, or error

    """
    if not is_valid_user(username, get_jwt_identity()):
        return abort(403, description='Identity does not match url path')

    schema = BookingSchema(exclude=['id', 'status', 'person'])
    try:
        booking = schema.loads(request.get_json())
    except ValidationError as ve:
        return abort(400, description='Invalid booking data')  # wow generic message

    # check that references to data in db is valid
    person = Person.query.filter_by(username=username).first()
    car = Car.query.filter_by(id=booking.car_id).first()
    if None in [person, car]:
        return abort(403, description='Booking references invalid id(s)')

    # Check that no booking with car is currently active
    if Booking.is_car_busy(booking.start_time, booking.end_time, booking.car_id):
        return abort(403, description=f'A booking with car id {booking.car_id}'
                                      f' is already mad in that time period')

    booking.person_id = person.id
    booking.status = BookingStatusEnum.ACTIVE

    # TODO: Add Google calendar event

    db.session.add(booking)
    db.session.commit()
    return schema.jsonify(booking), 201


@api_blueprint.route('/person/<string:username>/booking/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required
def deactivate_booking(username: str, id: int):
    """
    Deactivate a booking (cancel/finish)
    Args:
        username (str): username
        id (int): booking id

    Returns: Error if booking doesn't exist, or success message

    """
    if not is_valid_user(username, get_jwt_identity()):
        return abort(403, description='Identity does not match url path')

    booking = Booking.query.get(id)

    if booking is None or username != booking.person.username:
        return abort(403, description='Booking under wrong person')
    if request.method == 'PUT':
        booking.status = BookingStatusEnum.FINISHED
    else:
        booking.status = BookingStatusEnum.CANCELLED
        # TODO: Update Google calendar

    db.session.commit()
    return '', 200


@api_blueprint.route('/person/<string:username>/booking/<int:id>', methods=['GET'])
@jwt_required
def get_booking(username: str, id: int):
    """
    Get booking for given user and booking id

    Args:
        username: (str) logged in user
        id (int): booking id

    Returns: One booking if exists, else 404

    """
    if not is_valid_user(username, get_jwt_identity()):
        return abort(403, description='Identity does not match url path')

    schema = BookingSchema()
    booking = Booking.query.get(id)
    if booking is None or booking.person.username != username:
        return abort(404, description='Booking does not exist under this id/username!')

    person_json = PersonSchema().dumps(booking.person)
    car_json = CarSchema().dumps(booking.car)

    return jsonify({
        'booking': schema.dumps(booking),
        'person': person_json,
        'car': car_json
    }), 200

