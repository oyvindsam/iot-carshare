from flask import Blueprint, jsonify, request

from models import db, Person, PersonSchema

api = Blueprint('api', __name__)


@api.route('/person', methods=['GET'])
def get_persons():
    persons = Person.query.all()
    result = PersonSchema().dump(persons)

    return jsonify(result)


@api.route('/person', methods=['POST'])
def add_person():
    schema = PersonSchema()
    person = schema.load(request.get_json())
    db.session.add(person)
    db.session.commit()
    return schema.jsonify(person), 201