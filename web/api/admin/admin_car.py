import json

from flask import jsonify, request, abort
from marshmallow import ValidationError

from api import api_blueprint
from api.auth import role_required
from api.models import db, Car, PersonType, CarSchema, CarIssue, CarIssueSchema


@api_blueprint.route('/admin/car/<int:car_id>/issue', methods=['POST'])
@role_required(PersonType.ADMIN)
def issue(car_id: int):
    schema = CarIssueSchema(exclude=['id'])
    try:
        issue = schema.loads(request.get_json())
    except ValidationError as ve:
        return abort(400, description='Invalid issue data')
    car = Car.query.filter_by(id=car_id).first()
    if len(issue.issue) == 0:
        CarIssue.query.filter_by(id=car.issue.id).delete()
        db.session.commit()
        return jsonify('Issue deleted!'), 200

    db.session.add(issue)
    car.issue = issue
    db.session.commit()
    return jsonify('Issue updated'), 200


@api_blueprint.route('/admin/car/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@role_required(PersonType.ADMIN)
def car(id: int):
    schema = CarSchema()
    car = Car.query.get(id)
    if car is None:
        return abort(404, description='Car not found')
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