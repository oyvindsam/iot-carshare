from flask import jsonify, request, abort
from marshmallow import ValidationError
from sqlalchemy.exc import InvalidRequestError

from api import api_blueprint
from .models import db, Person, PersonSchema, PersonTypeSchema, BookingSchema, \
    Booking, Car, CarSchema, CarManufacturer, \
    CarManufacturerSchema, CarType, CarTypeSchema, CarColour, CarColourSchema, \
    BookingStatusEnum


# Url paths follows this pattern:
#
# POST /api/person (add a user)
# GET /api/person/<username> (get user details)
# GET/POST /api/cars (show all the available cars / search a car )
# POST /api/person/<username>/booking (book a car)
# GET /api/person/<username>/booking (view the history of my booked cars)
# PUT/DELETE /api/person/<username>/booking/<id> (finish/cancel a booking)
# GET /api/person/<username>/booking/<booking_id>
#
# All enpoints return a Flask Response object, either with error or success response
# success response usually have json data


# TODO: standarize error handling. https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages/
@api_blueprint.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


@api_blueprint.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e)), 400


@api_blueprint.errorhandler(409)
def conflict(e):
    return jsonify(error=str(e)), 409


# authorized
@api_blueprint.route('/person/<string:username>', methods=['GET'])
def get_person(username: str):
    """
    Get person data for logged in user

    Args:
        username (str): logged in user

    Returns: Response with person json string

    """
    persons = Person.query.filter_by(username=username).first()
    if persons is None:
        return abort(404, description='Person not found')
    result = PersonSchema().dumps(persons)

    return jsonify(result), 200


# add/create user
@api_blueprint.route('/person', methods=['POST'])
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
@api_blueprint.route('/person/<string:username>/booking', methods=['POST'])
def add_booking(username: str):
    """
    Add a new booking for this user
    Args:
        username (str): logged in user

    Returns: Json string of booking, or error

    """
    # bookings can't already have an id
    schema = BookingSchema(exclude=['id', 'status'])
    try:
        booking = schema.loads(request.get_json())
    except ValidationError as ve:
        return abort(400, description='Invalid booking data')  # wow generic message

    # check that references to data in db is valid

    # FIXME: this does not work when the references are wrong, wrap in try catch?
    # or change the ORM with less strict references.. For now do not give invalid parameters
    person = Person.query.filter_by(id=booking.person_id).first()
    car = Car.query.filter_by(id=booking.car_id).first()
    if None in [person, car]:
        return abort(403, description='Booking references invalid id(s)')

    if username != person.username:
        return abort(403, description='Booking under wrong person')

    # Check that no booking with car is currently active
    if Booking.is_car_busy(booking.start_time, booking.end_time, booking.car_id):
        return abort(403, description=f'A booking with car id {booking.car_id}'
                                      f' is already mad in that time period')

    booking.status = BookingStatusEnum.ACTIVE

    # TODO: Add Google calendar event

    db.session.add(booking)
    db.session.commit()
    return schema.jsonify(booking), 201


# Authorized
@api_blueprint.route('/person/<string:username>/booking/<int:id>', methods=['PUT', 'DELETE'])
def deactivate_booking(username: str, id: int):
    """
    Deactivate a booking (cancel/finish)
    Args:
        username (str): username
        id (int): booking id

    Returns: Error if booking doesn't exist, or success message

    """
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


# authorized!!
@api_blueprint.route('/person/<string:username>/booking', methods=['GET'])
def get_bookings(username: str):
    """
    Get all bookings for this user

    Args:
        username (str): logged in user

    Returns: All bookings for user with additional info as json list string, example:

    """

    schema = BookingSchema()
    person = Person.query.filter_by(username=username).first()
    if person is None:
        return abort(404, 'User not found')
    bookings = person.booking

    person_schema = PersonSchema()
    car_schema = CarSchema()

    data = [{
        'booking': schema.dumps(booking),
        'person': person_schema.dumps(booking.person),
        'car': car_schema.dumps(booking.car)
    }
        for booking in bookings]

    return jsonify(data), 200


# authorized!!
@api_blueprint.route('/person/<string:username>/booking/<int:id>', methods=['GET'])
def get_booking(username: str, id: int):
    """
    Get booking for given user and booking id

    Args:
        username: (str) logged in user
        id (int): booking id

    Returns: One booking if exists, else 404

    """
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


@api_blueprint.route('/car', methods=['GET', 'POST'])
def get_cars():
    """
    Get AVAILABLE cars based of query GET arguments/form POST arguments (supports both).
    All arguments must be in the Cars class otherwise a 404 is returned
    Example:
        GET /api/car?car_colour=1&car_manufacturer=2
        (note the id is used, not the name)

    Returns: Json list string of AVAILABLE Cars with given arguments
    """
    # From assignemnt doc: A car that is booked cannot be booked again until returned.
    # So a user can only look at cars that is not booked. Does not make sense but whatevs
    # So even if you want to book that car 50 days from now you are not able to.

    active_bookings = Booking.query.filter_by(status=BookingStatusEnum.ACTIVE)
    active_car_ids = set([b.car.id for b in active_bookings])
    available_cars = Car.query.filter(~Car.id.in_(active_car_ids))

    filters = request.values.to_dict()
    if len(filters) > 0:
        try:
            available_cars = available_cars.filter_by(**filters)
        except (InvalidRequestError, AttributeError):
            return abort(404, 'Query parameter(s)) invalid ')

    result = CarSchema(many=True).dumps(available_cars)
    return jsonify(result), 200


@api_blueprint.route('/car/<int:id>/location', methods=['PUT'])
def update_car_location(id: int):
    """
    Updates car in db (mainly for location).

    Args:
        id (int): car id
        json data contains 'latitude' and 'longitude' in float format

    Returns: updated car

    """
    car = Car.query.get(id)
    # Check car exists
    if car is None:
        return abort(404, description='Car not found')
    # Check location data is correct
    data = request.values.to_dict()
    if 'latitude' not in data or 'longitude' not in data:
        return abort(400, description='Missing location data')
    latitude = data['latitude'][:20]
    longitude = data['longitude'][:20]
    try:
        float(latitude)
        float(longitude)
    except ValueError:
        return abort(400, description='Invalid location data')
    car.latitude = latitude
    car.longitude = longitude
    db.session.commit()
    result = CarSchema().dumps(car)
    return jsonify(result), 200


@api_blueprint.route('/car-manufacturer', methods=['GET'])
def get_manufacturers():
    """
    Get all manufacturers

    Returns: All manufacturers as json list string

    """
    manufacturers = CarManufacturer.query.all()
    result = CarManufacturerSchema(many=True).dumps(manufacturers)
    return jsonify(result), 200


@api_blueprint.route('/car-type', methods=['GET'])
def get_car_types():
    """
    Get all car types

    Returns: All car types as json list string

    """
    types = CarType.query.all()
    result = CarTypeSchema(many=True).dumps(types)
    return jsonify(result), 200


@api_blueprint.route('/car-colour', methods=['GET'])
def get_car_colours():
    """
    Get all car colours.

    Returns: All car colours as json list string

    """
    colours = CarColour.query.all()
    result = CarColourSchema(many=True).dumps(colours)
    return jsonify(result), 200


# Admin endpoints, not neccessary for assignemnt 2.
# adding this data is allows to do manually
@api_blueprint.route('/person_type', methods=['POST'])
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


@api_blueprint.route('/person', methods=['GET'])
def get_persons():
    """
    Get all persons. For admins.

    Returns: All persons as json list string.

    """
    persons = Person.query.all()
    result = PersonSchema(many=True).dump(persons)
    return jsonify(result), 200
