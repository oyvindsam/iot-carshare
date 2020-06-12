from flask import jsonify, request, abort
from marshmallow import ValidationError

from api import api_blueprint
from api.auth import role_required
from api.models import db, Person, BookingSchema, \
    Booking, Car, PersonType, CarSchema, PersonSchema, CarManufacturerSchema


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
        return abort(400, description=ve.messages)  # wow generic message
    # check that references to data in db is valid
    person = Person.query.filter_by(id=booking.person_id).first()
    car = Car.query.filter_by(id=booking.car_id).first()
    if None in [person, car]:
        return abort(403, description='Booking references invalid person/car id(s)')

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
        'booking': BookingSchema().dump(booking),
        'person': PersonSchema().dump(booking.person),
        'car': CarSchema().dump(booking.car),
        'manufacturer': CarManufacturerSchema().dump(booking.car.manufacturer)
    } for booking in bookings]
    return jsonify(booking_data), 200


@api_blueprint.route('/booking/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@role_required(PersonType.ADMIN)
def booking(id: int):
    """
    Get, put, delete booking

    Args:
        id (int): booking id

    Returns: 403 if booking not found, 200 Ok

    """
    booking = Booking.query.get(id)
    if booking is None:
        return abort(403, description='Booking not found')

    if request.method == 'DELETE':
        Booking.query.filter_by(id=id).delete()
        db.session.commit()
        return jsonify('Booking deleted'), 200
    elif request.method == 'PUT':
        schema = BookingSchema()
        try:
            new_booking = schema.loads(request.get_json())
        except ValidationError as ve:
            return abort(403, description=ve.messages)

        booking.person_id = new_booking.person_id
        booking.car_id = new_booking.car_id
        booking.start_time = new_booking.start_time
        booking.end_time = new_booking.end_time
        booking.status = new_booking.status
        db.session.commit()
        return jsonify('Booking updated successfully'), 200
    else:
        schema = BookingSchema()
        return jsonify(schema.dumps(booking)), 200
