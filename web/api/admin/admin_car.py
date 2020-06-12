import json

from flask import jsonify, request, abort
from marshmallow import ValidationError

from api import api_blueprint
from api.api import handle_db_operation
from api.auth import role_required
from api.models import db, Car, PersonType, CarSchema, CarIssue, \
    CarIssueSchema, CarTypeSchema, CarManufacturerSchema, CarColourSchema


@api_blueprint.route('/admin/car/<int:car_id>/issue', methods=['POST'])
@role_required(PersonType.ADMIN)
def issue(car_id: int):
    """
    Endpoint to add/update/delete issue
    Args:
        car_id (int): car if for this issue (issue in one to one)

    Returns: 403

    """
    car = Car.query.filter_by(id=car_id).first()
    if car is None:
        return abort(404, description='Car not found')

    schema = CarIssueSchema(exclude=['id'])
    try:
        issue = schema.loads(request.get_json())
    except ValidationError as ve:
        return abort(400, description=ve.messages)

    # issue text is removed -> delete issue from db
    if len(issue.issue) == 0 and car.issue:
        CarIssue.query.filter_by(id=car.issue.id).delete()
        handle_db_operation(db.session.commit)
        return jsonify('Issue deleted!'), 200

    # add or update car issue
    db.session.add(issue)
    car.issue = issue

    handle_db_operation(db.session.commit)
    return jsonify('Issue updated'), 200


@api_blueprint.route('/admin/car/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@role_required(PersonType.ADMIN)
def car(id: int):
    """
    Get, update, or delete car
    Args:
        id (int): car id

    Returns: Error or 200

    """
    car = Car.query.get(id)
    if car is None:
        return abort(404, description='Car not found')
    schema = CarSchema()

    if request.method == 'GET':
        # Dump to dict, then add issue text
        car_data = schema.dump(car)
        if car.issue is not None:
            car_data['issue'] = car.issue.issue
        return jsonify(json.dumps(car_data)), 200

    elif request.method == 'PUT':
        try:
            new_car = schema.loads(request.get_json())
        except ValidationError as ve:
            return abort(400, description=ve.messages)

        car.reg_number = new_car.reg_number
        car.car_manufacturer = new_car.car_manufacturer
        car.car_colour = new_car.car_colour
        car.car_type = new_car.car_type
        car.seats = new_car.seats
        car.hour_rate = new_car.hour_rate
        car.longitude = new_car.longitude
        car.latitude = new_car.latitude

        handle_db_operation(db.session.commit)
        return jsonify('Car updated'), 200

    elif request.method == 'DELETE':
        Car.query.filter_by(id=id).delete()
        handle_db_operation(db.session.commit)
        return jsonify('Car deleted'), 200


@api_blueprint.route('/admin/car', methods=['GET'])
@role_required(PersonType.ADMIN)
def get_all_cars():
    """
    Endpoint to get all cars with extra data
    Returns: car data

    """
    cars = Car.query.all()
    car_data = [{
        'car': CarSchema().dump(car),
        'type': CarTypeSchema().dump(car.type),
        'manufacturer': CarManufacturerSchema().dump(car.manufacturer),
        'colour': CarColourSchema().dump(car.color)
    }
        for car in cars]
    return jsonify(car_data), 200


@api_blueprint.route('/admin/car', methods=['POST'])
@role_required(PersonType.ADMIN)
def add_car():
    """
    Endpoint to add car to db
    Returns: car added to db, or 400

    """
    schema = CarSchema(exclude=['id'])
    try:
        new_car = schema.loads(request.get_json())
    except ValidationError as ve:
        return abort(400, description=ve.messages)
    if Car.query.filter_by(reg_number=new_car.reg_number).first() is not None:
        return abort(403, description='Conflict, reg number exists!')
    db.session.add(new_car)
    handle_db_operation(db.session.commit)
    return jsonify(schema.dumps(new_car)), 201