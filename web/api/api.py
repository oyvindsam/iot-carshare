from flask import Blueprint, jsonify, request

from .models import db, Person, PersonSchema, PersonTypeSchema

api = Blueprint('api', __name__, url_prefix='/api/')


@api.route('/person', methods=['GET'])
def get_persons():
    persons = Person.query.all()
    result = PersonSchema().dump(persons)

    return jsonify(result)


@api.route('/person', methods=['POST'])
def add_person():
    schema = PersonSchema()
    print(request.get_json())
    person = schema.load(request.get_json())
    db.session.add(person)
    db.session.commit()
    return schema.jsonify(person), 201

@api.route('/person_type', methods=['POST'])
def add_person_type():
    schema = PersonTypeSchema()
    data = schema.loads(request.get_json())
    db.session.add(data)
    db.session.commit()
    return schema.jsonify(data), 201