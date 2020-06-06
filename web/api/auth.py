from functools import wraps

from flask import request, abort, jsonify
from flask_jwt_extended import jwt_required, create_access_token, \
    verify_jwt_in_request, get_jwt_claims, get_jwt_identity
from marshmallow import ValidationError
from werkzeug.security import check_password_hash, generate_password_hash

from api import api_blueprint, jwt
from api.booking import is_valid_user
from api.models import Person, PersonSchema, db, PersonType


# Read up on how to create token with user id and roles
# https://flask-jwt-extended.readthedocs.io/en/stable/tokens_from_complex_object/
@jwt.user_claims_loader
def add_claims_to_access_token(person: Person):
    return person.type

@jwt.user_identity_loader
def user_identity_lookup(person: Person):
    return person.username


@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    return Person.query.filter_by(username=identity)


def role_required(roles):
    """
    Use this as a decorator to verify that user has correct roles
    Args:
        roles (list[str]): roles required, e.g. 'CUSTOMER'

    Returns: wrapped function, or error

    """
    def check_role(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claim = get_jwt_claims()  # currently only one role per user
            if claim not in roles:
                return jsonify(msg='Does not have permission to access this endpoint!'), 403
            else:
                return fn(*args, **kwargs)
        return wrapper
    return check_role


@api_blueprint.route('/auth/register', methods=['POST'])
def register_user():
    """
    Get user details from http form post and creates user
    Returns: success message, or error

    """
    data = request.get_json()
    schema = PersonSchema(exclude=['id', 'type'])
    try:
        person = schema.load(request.get_json())
    except ValidationError:
        return abort(400, description='Invalid person data')
    if Person.query.filter_by(username=person.username).first() is not None:
        return abort(409, description='User exists')

    # the passed password is not hashed, hash it.
    person.password = generate_password_hash(person.password)

    db.session.add(person)
    db.session.commit()

    return jsonify('User created!'), 201


@api_blueprint.route('/auth/login', methods=['POST'])
def login_user():
    """
    Get user username and password from form post, try to log in user.
    Returns: http 200 response with json data with token, and user details

    """
    data = request.get_json()
    username, password = data.get('username', None), data.get('password', None)
    if username is None or password is None:
        return abort(400, description='Invalid data passed')

    # check if user exists, then check password
    person = Person.query.filter_by(username=username).first()
    if person is None or not check_password_hash(person.password, password):
        return abort(403, 'Invalid username or password')

    # currently the token does not expire!
    access_token = create_access_token(identity=person, expires_delta=False)
    response = {
        'access_token': access_token,
        'username': person.username,
        'type': person.type,
        'email': person.email
    }
    return jsonify(response), 200

