from flask import request, abort
from flask_jwt_extended import create_access_token, create_refresh_token
from marshmallow import ValidationError
from werkzeug.security import check_password_hash, generate_password_hash

from api import auth, api_blueprint
from api.models import Person, PersonSchema, PersonType, db


@api_blueprint.route('register', methods=['POST'])
def register_user():
    schema = PersonSchema(exclude=['id', 'person_type'])
    try:
        person = schema.loads(request.get_json())
    except ValidationError:
        return abort(400, description='Invalid person data')
    if Person.query.filter_by(username=person.username).first() is not None:
        return abort(409, description='User exists')

    # the passed password is not hashed, hash it.
    person.password_hashed = generate_password_hash(person.password_hashed)

    db.session.add(person)
    db.session.commit()

    return {'User created!'}, 201


@api_blueprint.route('login', methods=['POST'])
def login_user():
    data = request.get_json()
    username, password = data.get('username', None), data.get('password', None)
    if username is None or password is None:
        return abort(400, description='Invalid data passed')

    # check if user exists, then check password
    person = Person.query.filter_by(username=username).first()
    if person is None or not check_password_hash(person.password_hashed, password):
        return abort(403, 'Invalid username or password')

    access_token = create_access_token(identity=person.id, expires_delta=False)
    refresh_token = create_refresh_token(identity=person.id)
    return {
        'message': 'Logged in as {}'.format(person.username),
        'access_token': access_token,
        'refresh_token': refresh_token
    }