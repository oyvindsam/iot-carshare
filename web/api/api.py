from flask import jsonify, request, abort
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import InvalidRequestError

from api import api_blueprint, jwt
from .auth import role_required
from .booking import is_valid_user
from .models import db, Person, PersonSchema, Booking, Car, CarSchema, \
    CarManufacturer, \
    CarManufacturerSchema, CarType, CarTypeSchema, CarColour, CarColourSchema, \
    BookingStatusEnum, PersonType


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
@api_blueprint.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e)), 400


@api_blueprint.errorhandler(403)
def bad_request(e):
    return jsonify(error=str(e)), 403


@api_blueprint.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


@api_blueprint.errorhandler(409)
def conflict(e):
    return jsonify(error=str(e)), 409


@api_blueprint.route('/person/<string:username>', methods=['GET'])
@role_required([PersonType.CUSTOMER, PersonType.ADMIN])
def get_person(username: str):
    """
    Get person data for logged in user

    Args:
        username (str): logged in user

    Returns: Response with person json string

    """
    if not is_valid_user(username, get_jwt_identity()):
        return abort(403, description='Identity does not match url path')
    persons = Person.query.filter_by(username=username).first()
    if persons is None:
        return abort(404, description='Person not found')
    result = PersonSchema().dumps(persons)

    return jsonify(result), 200


@api_blueprint.route('/car', methods=['GET', 'POST'])
@jwt_required
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
#@jwt_required
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
@jwt_required
def get_manufacturers():
    """
    Get all manufacturers

    Returns: All manufacturers as json list string

    """
    manufacturers = CarManufacturer.query.all()
    result = CarManufacturerSchema(many=True).dumps(manufacturers)
    return jsonify(result), 200


@api_blueprint.route('/car-type', methods=['GET'])
@jwt_required
def get_car_types():
    """
    Get all car types

    Returns: All car types as json list string

    """
    types = CarType.query.all()
    result = CarTypeSchema(many=True).dumps(types)
    return jsonify(result), 200


@api_blueprint.route('/car-colour', methods=['GET'])
@jwt_required
def get_car_colours():
    """
    Get all car colours.

    Returns: All car colours as json list string

    """
    colours = CarColour.query.all()
    result = CarColourSchema(many=True).dumps(colours)
    return jsonify(result), 200


@api_blueprint.route('/person', methods=['GET'])
@role_required([PersonType.ADMIN])
def get_persons():
    """
    Get all persons. For admins.

    Returns: All persons as json list string.

    """
    persons = Person.query.all()
    result = PersonSchema(many=True).dump(persons)
    return jsonify(result), 200
