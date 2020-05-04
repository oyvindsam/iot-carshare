from flask import Blueprint, jsonify, request, abort
from flask_marshmallow import Schema

from .models import db, Person, PersonSchema, PersonTypeSchema, BookingSchema

api = Blueprint('api', __name__, url_prefix='/api/')


@api.route('/person', methods=['GET'])
def get_persons():
    persons = Person.query.all()
    result = PersonSchema().dump(persons)

    return jsonify(result), 200


@api.route('/person/<string:username>', methods=['GET'])
def get_person(username: str):
    persons = Person.query.filter_by(username=username).first()
    result = PersonSchema().dumps(persons)

    return jsonify(result), 200


@api.route('/person', methods=['POST'])
def add_person():
    schema = PersonSchema()
    person = schema.loads(request.get_json())
    if person.id is not None:
        return abort(409)
    db.session.add(person)
    db.session.commit()
    return schema.jsonify(person), 201


@api.route('/person_type', methods=['POST'])
def add_person_type():
    schema = PersonTypeSchema()
    person_type = schema.loads(request.get_json())
    db.session.add(person_type)
    db.session.commit()
    return schema.jsonify(person_type), 201


@api.route('/booking', methods=['POST'])
def add_booking():
    schema = BookingSchema()
    booking = schema.loads(request.get_json())
    if booking.id is not None:
        return abort(409)
    db.session.add(booking)
    db.session.commit()
    return schema.jsonify(booking), 201

