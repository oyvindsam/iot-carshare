from flask import jsonify, request, abort
from marshmallow import ValidationError

from api import api_blueprint
from .auth import role_required
from .models import db, Person, BookingSchema, \
    Booking, Car, PersonType, CarSchema


@api_blueprint.route('/booking', methods=['POST'])
@role_required(PersonType.ADMIN)
def add_booking_admin():
    """
    Add a new booking

    Returns: Json string of booking, or error

    """

    schema = BookingSchema(exclude=['id'])
    try:
        booking = schema.loads(request.get_json())
    except ValidationError as ve:
        return abort(400, description='Invalid booking data')  # wow generic message
    # check that references to data in db is valid
    person = Person.query.filter_by(id=booking.person_id).first()
    car = Car.query.filter_by(id=booking.car_id).first()
    if None in [person, car]:
        return abort(403, description='Booking references invalid id(s)')

    # Check that no booking with car is currently active
    if Booking.is_car_busy(booking.start_time, booking.end_time, booking.car_id):
        return abort(403, description=f'A booking with car id {booking.car_id}'
                                      f' is already mad in that time period')

    db.session.add(booking)
    db.session.commit()
    return schema.jsonify(booking), 201


@api_blueprint.route('/booking', methods=['GET'])
@role_required([PersonType.ADMIN])
def get_all_bookings_details():
    """
    Get all bookings

    Returns: All bookings details in list of objects

    """
    bookings = Booking.query.all()
    booking_data = [{
        'booking_id': booking.id,
        'person_id': booking.person_id,
        'person_username': booking.person.username,
        'person_first_name': booking.person.first_name,
        'person_last_name': booking.person.last_name,
        'car_id': booking.car_id,
        'booking_start_time': booking.start_time,
        'booking_end_time': booking.end_time,
        'booking_status': booking.status
    } for booking in bookings]
    return jsonify(booking_data), 200


@api_blueprint.route('/booking/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@role_required(PersonType.ADMIN)
def booking(id: int):
    """
    Get booking for given user and booking id

    Args:
        username: (str) logged in user
        id (int): booking id

    Returns: One booking if exists, else 404

    """
    # TODO: add? validate object exists
    if request.method == 'DELETE':
        Booking.query.filter_by(id=id).delete()
        db.session.commit()
        return jsonify('Booking deleted'), 200
    elif request.method == 'PUT':
        schema = BookingSchema()
        new_booking = schema.loads(request.get_json())
        booking = Booking.query.get(new_booking.id)
        booking.person_id = new_booking.person_id
        booking.car_id = new_booking.car_id
        booking.start_time = new_booking.start_time
        booking.end_time = new_booking.end_time
        booking.status = new_booking.status
        db.session.commit()
        return jsonify('Booking updated successfully'), 200
    else:
        schema = BookingSchema()
        booking = Booking.query.get(id)
        return jsonify(schema.dumps(booking)), 200


@api_blueprint.route('/admin/car/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@role_required(PersonType.ADMIN)
def car(id: int):
    schema = CarSchema()
    car = Car.query.get(id)
    if car is None:
        return abort(404, description='Car not found')
    if request.method == 'GET':
        return jsonify(schema.dumps(car)), 200

    elif request.method == 'PUT':
        try:
            new_car = schema.loads(request.get_json())
        except ValidationError as ve:
            return abort(400, description='Invalid car data')

        car.reg_number = new_car.reg_number
        car.car_manufacturer = new_car.car_manufacturer
        car.car_colour = new_car.car_colour
        car.car_type = new_car.car_type
        car.seats = new_car.seats
        car.hour_rate = new_car.hour_rate
        car.longitude = new_car.longitude
        car.latitude = new_car.latitude

        db.session.commit()
        return jsonify('Car updated'), 200

    elif request.method == 'DELETE':
        Car.query.filter_by(id=id).delete()
        db.session.commit()
        return jsonify('Car deleted'), 200


@api_blueprint.route('/admin/car', methods=['GET'])
@role_required(PersonType.ADMIN)
def get_all_cars():

    schema = CarSchema(many=True)
    cars = Car.query.all()
    return jsonify(schema.dumps(cars)), 200


@api_blueprint.route('/admin/car', methods=['POST'])
@role_required(PersonType.ADMIN)
def add_car():

    schema = CarSchema(exclude=['id'])
    try:
        new_car = schema.loads(request.get_json())
    except ValidationError as ve:
        return abort(400, description=ve.messages)

    db.session.add(new_car)
    db.session.commit()

    return jsonify(schema.dumps(new_car)), 201