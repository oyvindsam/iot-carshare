from functools import wraps

from flask import request, abort, jsonify
from flask_jwt_extended import jwt_required, create_access_token, \
    verify_jwt_in_request, get_jwt_claims
from marshmallow import ValidationError
from werkzeug.security import check_password_hash, generate_password_hash

from api import api_blueprint, jwt
from api.models import Person, PersonSchema, db

# Read up on how to create token with user id and roles
# https://flask-jwt-extended.readthedocs.io/en/stable/tokens_from_complex_object/

@jwt.user_claims_loader
def add_claims_to_access_token(person: Person):
    """
    Returns user role (person type)

    Args:
        person (Person): person who generates token

    Returns: roles for this user

    """
    return person.person_type

@jwt.user_identity_loader
def user_identity_lookup(person: Person):
    """
    Find identity from user object
    Args:
        person (Person): person who generates token

    Returns: user id

    """
    return person.id


@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    return Person.query.get(identity)


def role_required(roles):
    def check_role(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt_claims()
            if claims['roles'] not in roles:
                return jsonify(msg='Does not have permission to access this endpoint!'), 403
            else:
                return fn(*args, **kwargs)
        return wrapper
    return check_role



@api_blueprint.route('/auth/register', methods=['POST'])
def register_user():
    data = request.get_json()
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

    return jsonify('User created!'), 201


@api_blueprint.route('/auth/login', methods=['POST'])
def login_user():
    data = request.get_json()
    username, password = data.get('username', None), data.get('password', None)
    if username is None or password is None:
        return abort(400, description='Invalid data passed')

    # check if user exists, then check password
    person = Person.query.filter_by(username=username).first()
    if person is None or not check_password_hash(person.password_hashed, password):
        return abort(403, 'Invalid username or password')

    access_token = create_access_token(identity=person, expires_delta=False)
    return jsonify(access_token=access_token), 200

