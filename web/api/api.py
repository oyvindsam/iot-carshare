from flask import Blueprint, jsonify, request, abort
from marshmallow import ValidationError
from sqlalchemy.exc import InvalidRequestError

from .models import db, Person, PersonSchema, PersonTypeSchema, BookingSchema, \
    Booking, Car, BookingStatus, CarSchema, CarManufacturer, \
    CarManufacturerSchema, CarType, CarTypeSchema, CarColour, CarColourSchema, \
    BookingStatusSchema

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
    """
    Get person data for logged in user

    Args:
        username: logged in user

    Returns: Person json string

    """
    persons = Person.query.filter_by(username=username).first()
    if persons is None:
        return abort(404, description='Person not found')
    result = PersonSchema().dumps(persons)

    return jsonify(result), 200


# add/create user
@api.route('/person', methods=['POST'])
def add_person():
    """
    Add a new person to db, or error if username already taken

    Returns: Json string of added user

    """
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
    """
    Add a new booking for this user
    Args:
        username: logged in user

    Returns: Json string of booking, or error

    """
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

    # Check that no booking with car is currently active
    if any([b.car_id == car.id for b in Booking.filter_by_is_active()]):
        return abort(403, description='A booking with this car is already in session')

    db.session.add(booking)
    db.session.commit()
    return schema.jsonify(booking), 201


# TODO: Test
# authorized!!
@api.route('/person/<string:username>/booking', methods=['GET'])
def get_bookings(username: str):
    """
    Get all bookings for this user
    Args:
        username: logged in user

    Returns: All bookings for user, or 404

    """
    schema = BookingSchema(many=True)
    person = Person.query.filter_by(username=username).first()
    if person is None:
        return abort(404, 'User not found')
    booking = person.booking

    return schema.jsonify(booking), 200


# authorized!!
@api.route('/person/<string:username>/booking/<int:id>', methods=['GET'])
def get_booking(username: str, id: int):
    """
    Get booking for given user and booking id

    Args:
        username: logged in user
        id: booking id

    Returns: One booking if exists, else 404

    """
    schema = BookingSchema()
    booking = Booking.query.get(id)
    if booking is None or booking.person.username != username:
        return abort(404, description='Booking does not exist under this id/username!')

    return schema.jsonify(booking), 200


@api.route('/car', methods=['GET', 'POST'])
def get_cars():
    """
    Get cars based of query GET arguments/form POST arguments (supports both).
    All arguments must be in the Cars class otherwise a 404 is returned
    Example:
        GET /api/car?car_colour=1&car_manufacturer=2
        (note the id is used, not the name)

    Returns: Json list string of Cars with given arguments
    """
    filters = request.values.to_dict()
    if len(filters) > 0:
        try:
            cars = Car.query.filter_by(**filters)
        except (InvalidRequestError, AttributeError):
            return abort(404, 'Query parameter(s)) invalid ')
    else:
        cars = Car.query.all()
    result = CarSchema(many=True).dumps(cars)
    return jsonify(result), 200


@api.route('/car-manufacturer', methods=['GET'])
def get_manufacturers():
    """
    Get all manufacturers

    Returns: All manufacturers as json list string

    """
    manufacturers = CarManufacturer.query.all()
    result = CarManufacturerSchema(many=True).dumps(manufacturers)
    return jsonify(result), 200


@api.route('/car-type', methods=['GET'])
def get_car_types():
    """
    Get all car types

    Returns: All car types as json list string

    """
    types = CarType.query.all()
    result = CarTypeSchema(many=True).dumps(types)
    return jsonify(result), 200


@api.route('/car-colour', methods=['GET'])
def get_car_colours():
    """
    Get all car colours.

    Returns: All car colours as json list string

    """
    colours = CarColour.query.all()
    result = CarColourSchema(many=True).dumps(colours)
    return jsonify(result), 200


@api.route('/booking-status', methods=['GET'])
def get_booking_statuses():
    """
    Get all booking statuses

    Returns: All booking statuses as json list string

    """
    statuses = BookingStatus.query.all()
    result = BookingStatusSchema(many=True).dumps(statuses)
    return jsonify(result), 200


# Admin endpoints, not neccessary for assignemnt 2.
# adding this data is allows to do manually
@api.route('/person_type', methods=['POST'])
def add_person_type():
    """
    Add person type. For admins.

    Returns: Added person type as json string.

    """
    schema = PersonTypeSchema()
    person_type = schema.loads(request.get_json())
    db.session.add(person_type)
    db.session.commit()
    return schema.jsonify(person_type), 201


@api.route('/person', methods=['GET'])
def get_persons():
    """
    Get all persons. For admins.

    Returns: All persons as json list string.

    """
    persons = Person.query.all()
    result = PersonSchema(many=True).dump(persons)
    return jsonify(result), 200
