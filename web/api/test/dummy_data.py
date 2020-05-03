import json

from api.models import PersonType, Person


class DummyPerson:

    p1 = Person(
        username='test',
        first_name='first',
        last_name='last',
        email='test@gmail.com',
        person_type=1,
        password_hashed='password',
        face=None
    )

    p2 = Person(
        username='test2',
        first_name='first2',
        last_name='last2',
        email='test2@gmail.com',
        person_type=1,
        password_hashed='password',
        face=None
    )

    p1_json = json.dumps({
        'id': 1,
        'username': 'test',
        'first_name': 'first',
        'last_name': 'last',
        'email': 'test@gmail.com',
        'person_type': 1,
        'password_hashed': 'password',
        'face': ''
    })


class DummyPersonType:
    c1 = PersonType(
        id=1,
        type='Customer'
    )

    c1_json = json.dumps({
        'id': 1,
        'type': 'Customer'
    })