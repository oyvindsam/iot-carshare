import json

from flask import jsonify, request, abort
from marshmallow import ValidationError

from api import api_blueprint
from api.auth import role_required
from api.models import db, Car, PersonType, CarSchema, CarIssue, \
    CarIssueSchema, CarTypeSchema, CarManufacturerSchema, CarColourSchema


@api_blueprint.route('/engineer/car', methods=['GET'])
@role_required([PersonType.ADMIN, PersonType.ENGINEER])
def get_all_cars_with_issue():
    """
    Endpoint to get all cars with issue data
    Returns: car data

    """
    issues = CarIssue.query.all()
    car_issue = [issue.car for issue in issues]
    car_data = [{
        'car': CarSchema().dump(car),
        'issue': CarIssueSchema().dump(car.issue),
        'type': CarTypeSchema().dump(car.type),
        'manufacturer': CarManufacturerSchema().dump(car.manufacturer),
        'colour': CarColourSchema().dump(car.color)
    }
        for car in car_issue]
    return jsonify(car_data), 200
