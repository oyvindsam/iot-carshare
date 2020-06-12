import json

from flask import jsonify, request, abort
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash

from api import api_blueprint
from api.api import handle_db_operation
from api.auth import role_required
from api.models import db, PersonType, PersonSchema, Person


@api_blueprint.route('/admin/person/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@role_required(PersonType.ADMIN)
def person(id: int):
    """
    Endpoint to get/update/delete person
    Args:
        id (int): person id

    Returns: Error or 200 if task successful

    """
    person = Person.query.get(id)
    if person is None:
        return abort(404, description='Person not found')
    schema = PersonSchema()
    if request.method == 'GET':
        person_data = schema.dump(person)
        return jsonify(json.dumps(person_data)), 200

    elif request.method == 'PUT':
        try:
            new_person = schema.loads(request.get_json())
        except ValidationError as ve:
            return abort(400, description=ve.messages)
        person.username = new_person.username
        person.first_name = new_person.first_name
        person.last_name = new_person.last_name
        person.email = new_person.email
        person.type = new_person.type
        person.type = new_person.type

        # check if password is plaintext or hashed
        if not new_person.password.startswith('pbkdf2'):
            person.password = generate_password_hash(new_person.password)
        else:
            person.password = new_person.password

        handle_db_operation(db.session.commit)
        return jsonify('Person updated'), 200

    elif request.method == 'DELETE':
        Person.query.filter_by(id=id).delete()
        handle_db_operation(db.session.commit)
        return jsonify('Person deleted'), 200


@api_blueprint.route('/admin/person', methods=['GET'])
@role_required(PersonType.ADMIN)
def get_all_persons():
    """
    Endpoint to get all persons
    Returns: all persons

    """
    schema = PersonSchema(many=True)
    persons = Person.query.all()
    return jsonify(schema.dumps(persons)), 200


@api_blueprint.route('/admin/person', methods=['POST'])
@role_required(PersonType.ADMIN)
def add_person():
    """
    Endpoint to add a person
    Returns: Updated person 201, or invalid data error

    """
    schema = PersonSchema(exclude=['id'])
    try:
        new_person = schema.loads(request.get_json())
    except ValidationError as ve:
        return abort(400, description=ve.messages)
    # if password not on correct hash format, hash it
    if not new_person.password.startswith('pbkdf2'):
        new_person.password = generate_password_hash(new_person.password)
    db.session.add(new_person)
    handle_db_operation(db.session.commit)

    return jsonify(schema.dumps(new_person)), 201