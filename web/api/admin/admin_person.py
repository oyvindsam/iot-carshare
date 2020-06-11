import json

from flask import jsonify, request, abort
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash

from api import api_blueprint
from api.auth import role_required
from api.models import db, PersonType, PersonSchema, Person


@api_blueprint.route('/admin/person/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@role_required(PersonType.ADMIN)
def person(id: int):
    schema = PersonSchema()
    person = Person.query.get(id)
    if person is None:
        return abort(404, description='Person not found')
    if request.method == 'GET':
        # Dump to dict, then add issue text
        person_data = schema.dump(person)
        return jsonify(json.dumps(person_data)), 200

    elif request.method == 'PUT':
        try:
            new_person = schema.loads(request.get_json())
        except ValidationError as ve:
            return abort(400, description=ve.messages)

        db.session.commit()
        return jsonify('Person updated'), 200

    elif request.method == 'DELETE':
        Person.query.filter_by(id=id).delete()
        db.session.commit()
        return jsonify('Person deleted'), 200


@api_blueprint.route('/admin/person', methods=['GET'])
@role_required(PersonType.ADMIN)
def get_all_persons():
    schema = PersonSchema(many=True)
    persons = Person.query.all()
    return jsonify(schema.dumps(persons)), 200


@api_blueprint.route('/admin/person', methods=['POST'])
@role_required(PersonType.ADMIN)
def add_person():
    schema = PersonSchema(exclude=['id'])
    try:
        new_person = schema.loads(request.get_json())
    except ValidationError as ve:
        return abort(400, description=ve.messages)
    # if password not on correct hash format, hash it
    if not new_person.password.startswith('pbkdf2'):
        new_person.password = generate_password_hash(new_person.password)
    db.session.add(new_person)
    db.session.commit()

    return jsonify(schema.dumps(new_person)), 201