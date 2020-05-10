from unittest import TestCase

from flask import Flask
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from api.api import api
from api.models import db, PersonSchema, BookingSchema, CarSchema
from api.test.dummy_data import *


def get_test_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:?cache=shared'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    db.init_app(app)
    app.register_blueprint(api)
    with app.app_context():
        db.create_all()
    return app


class DatabaseTest(TestCase):

    def setUp(self) -> None:
        self.app = get_test_app()

    def test_add_person_to_db(self):
        with self.app.app_context():
            db.session.add(DummyPerson.person_customer1)
            db.session.add(DummyPerson.person_customer2)
            db.session.commit()
            p1 = Person.query.filter_by(username=DummyPerson.person_customer1.username).first()
            p2 = Person.query.filter_by(username=DummyPerson.person_customer2.username).first()
            self.assertEqual(p1.username, DummyPerson.person_customer1.username)
            self.assertTrue(p1.id < p2.id)


class ApiTest(TestCase):

    def setUp(self) -> None:
        """
        Testing with SQLAlchemy objects is a mess. What works is instead of
        saving the reference to the db object in setUp, the id is saved instead.
        Then in the test method you have to query on the id to get the
        reference to the db object.

        """
        self.app = get_test_app()

        with self.app.app_context():
            # Note: self.type1 is the id (int), not a object.
            self.type1 = add_to_db(DummyCarType.create_random()).id
            self.type2 = add_to_db(DummyCarType.create_random()).id
            self.manufacturer1 = add_to_db(DummyCarManufacturer.create_random()).id
            self.manufacturer2 = add_to_db(DummyCarManufacturer.create_random()).id
            self.colour1 = add_to_db(DummyCarColour.create_random()).id
            self.colour2 = add_to_db(DummyCarColour.create_random()).id

            car1 = DummyCar.create_random()
            car2 = DummyCar.create_random()
            car3 = DummyCar.create_random()

            car1.car_type = self.type1
            car1.car_manufacturer = self.manufacturer1
            car1.car_colour = self.colour1
            car2.car_type = self.type1
            car2.car_manufacturer = self.manufacturer1
            car2.car_colour = self.colour1

            car3.car_type = self.type1  # Same
            car3.car_colour = self.colour2  # Different than the others
            car3.car_manufacturer = self.manufacturer2  # Different than the others

            # Finally add cars with correct foreign keys
            self.car1 = add_to_db(car1).id
            self.car2 = add_to_db(car2).id
            self.car3 = add_to_db(car3).id

    # Person tests

    def test_add_person_type(self):
        with self.app.test_client() as app:
            response = app.post('/api/person_type', json=DummyPersonType.pt_customer_no_id_json)
            self.assertEqual(response.status_code, 201)

    # id is automatically added by the db
    def test_cant_add_person_with_id(self):
        with self.app.test_client() as app:
            response_post = app.post('/api/person', json=DummyPerson.p1_id_json)
            self.assertEqual(response_post.status_code, 400)


    def test_add_get_person(self):
        with self.app.test_client() as app:

            response_post = app.post('/api/person', json=DummyPerson.p1_no_id_json)
            self.assertEqual(response_post.status_code, 201)

            response_get = app.get(f'/api/person/{DummyPerson.person_customer1.username}')
            self.assertEqual(response_get.status_code, 200)

    def test_get_invalid_person(self):
        with self.app.test_client() as app:

            response_get = app.get('/api/person/userthatdontexist')

            self.assertEqual(response_get.status_code, 404)

    def test_add_invalid_person_raises_error(self):
        with self.app.test_client() as app:
            # empty first_name among other missing fields
            invalid_person = json.dumps({'username': 'valid', 'first_name': ''})
            response = app.post('/api/person', json=invalid_person)
            self.assertTrue(response.status_code, 404)

    def test_add_two_persons_with_same_username_raises_error(self):
        with self.app.test_client() as app:
            person = DummyPerson.p1_no_id_json

            person['username']: uuid4().__str__()
            response_valid = app.post('/api/person', json=person)
            response_error = app.post('/api/person', json=person)
            self.assertEqual(response_valid.status_code, 201)
            self.assertEqual(response_error.status_code, 409)

    # Booking tests

    def test_add_booking(self):
        with self.app.app_context():
            # set up db for booking
            person1 = add_to_db(DummyPerson.create_random())
            person_type1 = add_to_db(DummyPersonType.create_random())
            person1.person_type = person_type1.id

            car = add_to_db(DummyCar.create_random())
            car_type = add_to_db(DummyCarType.create_random())
            manufacturer = add_to_db(DummyCarManufacturer.create_random())
            car_colour = add_to_db(DummyCarColour.create_random())
            car.car_type = car_type.id
            car.car_manufacturer = manufacturer.id
            car.car_colour = car_colour.id

            booking = DummyBooking.person1_car1_available
            booking_status = add_to_db(DummyBookingStatus.create_random())
            booking.car_id = car.id
            booking.person_id = person1.id
            booking.status_id = booking_status.id

            with self.app.test_client() as app:
                # serialize booking to json str
                booking_jsonstr = json.dumps(BookingSchema(exclude=['id']).dump(booking))

                response_valid = app.post(f"/api/person/{person1.username}/booking", json=booking_jsonstr)
                self.assertEqual(response_valid.status_code, 201)

                # post to username that does not match booking person username
                response_wrong_username = app.post(f"/api/person/wrongusername/booking", json=booking_jsonstr)
                self.assertEqual(response_wrong_username.status_code, 403)

                # give valid data that does not match db
                booking.car_id = -1
                booking_jsonstr = json.dumps(BookingSchema(exclude=['id']).dump(booking))
                response_invalid_data = app.post(f"/api/person/{person1.username}/booking", json=booking_jsonstr)
                self.assertEqual(response_invalid_data.status_code, 400)

                # give invalid data (missing car id)
                booking_jsonstr = json.dumps({
                    'car_id': '',
                    'person_id': 1,
                    'start_time': '2020-05-03T21:2',
                    'end_time': '2020-05-04T02:2',
                    'status_id': 1
                })
                response_invalid_data = app.post(f"/api/person/{person1.username}/booking",json=booking_jsonstr)
                self.assertEqual(response_invalid_data.status_code, 400)

                # this pattern might work better than having gigantic test methods
                def get_booking():
                    response_get = app.get(f'/api/person/{person1.username}/booking')
                    self.assertEqual(response_get.status_code, 200)
                #get_booking()

    def test_get_all_cars(self):
        with self.app.app_context():
            with self.app.test_client() as app:
                response = app.get('/api/car', query_string={})
                self.assertEqual(200, response.status_code)
                response_cars = CarSchema(many=True).loads(response.get_json())
                self.assertTrue(type(Car), type(response_cars[0]))

    def test_get_filtered_cars(self):
        with self.app.app_context():
            with self.app.test_client() as app:
                colour1 = CarColour.query.get(self.colour1)
                manufacturer1 = CarManufacturer.query.get(self.manufacturer1)
                car3 = Car.query.get(self.car3)
                filters = {
                    'car_colour': colour1.id,
                    'car_manufacturer': manufacturer1.id
                }
                response = app.get('/api/car', query_string=filters)
                self.assertEqual(200, response.status_code)

                response_cars = CarSchema(many=True).loads(response.get_json())
                self.assertTrue(type(Car), type(response_cars[0]))
                self.assertTrue(all([car.car_colour == self.colour1 for car in response_cars]))
                self.assertTrue(self.car3 not in response_cars)

    def test_get_invalid_filtered_cars(self):
        with self.app.app_context():
            with self.app.test_client() as app:
                # cannot filter on 'color', use 'car_colour'
                filters = {
                    'colour': 'White'
                }
                response = app.get('/api/car', query_string=filters)
                self.assertEqual(404, response.status_code)

                # add invalid query parameters
                filters = {
                    'car_colour': self.colour1,
                    'invalid': 'invalid'
                }
                response = app.get('/api/car', query_string=filters)
                self.assertEqual(404, response.status_code)


# by calling commit 'thing' will be assigned an id
def add_to_db(thing):
    db.session.add(thing)
    db.session.commit()
    return thing


class ModelTest(TestCase):
    def setUp(self) -> None:
        self.app = get_test_app()

    def test_person_type_relationship(self):
        with self.app.app_context():
            p1 = add_to_db(DummyPerson.create_random())
            p2 = add_to_db(DummyPerson.create_random())
            pt1 = add_to_db(DummyPersonType.create_random())

            p1.person_type = pt1.id
            p2.person_type = pt1.id

            self.assertEqual(Person.query.filter_by(username=p1.username).first().type.id, pt1.id)
            self.assertEqual(Person.query.filter_by(username=p2.username).first().type.id, pt1.id)
            # check that person1 and person2 are in the list of persons backreferenced from personType
            self.assertTrue(set([p1, p2]) <= set(PersonType.query.filter_by(id=pt1.id).first().person))

    def test_car_relationships(self):
        with self.app.app_context():
            car = add_to_db(DummyCar.create_random())
            car_type = add_to_db(DummyCarType.create_random())
            manufacturer = add_to_db(DummyCarManufacturer.create_random())

            # be sure id point to valid type/manufacturer
            car.car_type = car_type.id
            car.car_manufacturer = manufacturer.id

            # check references to/from car/carType/carManufacturer
            self.assertEqual(car.type, car_type)
            self.assertTrue(car in car.manufacturer.car)

            self.assertEqual(Car.query.filter_by(reg_number=car.reg_number).first().type.id, car_type.id)
            self.assertEqual(Car.query.filter_by(reg_number=car.reg_number).first().manufacturer.id, manufacturer.id)
            self.assertTrue(set([car]) <= set(CarManufacturer.query.filter_by(manufacturer=manufacturer.manufacturer).first().car))
            self.assertTrue(set([car]) <= set(CarType.query.filter_by(type=car_type.type).first().car))

    def test_booking_relationships(self):
        with self.app.app_context():
            # set up objects and relationships
            person1 = add_to_db(DummyPerson.create_random())
            person_type1 = add_to_db(DummyPersonType.create_random())
            person1.person_type = person_type1.id

            car = add_to_db(DummyCar.create_random())
            car_type = add_to_db(DummyCarType.create_random())
            manufacturer = add_to_db(DummyCarManufacturer.create_random())
            car_colour = add_to_db(DummyCarColour.create_random())
            car.car_type = car_type.id
            car.car_manufacturer = manufacturer.id
            car.car_colour = car_colour.id

            booking = add_to_db(DummyBooking.person1_car1_available)
            booking_status = add_to_db(DummyBookingStatus.create_random())
            booking.car_id = car.id
            booking.person_id = person1.id
            booking.status_id = booking_status.id

            self.assertEqual(booking.status, booking_status)
            self.assertEqual(booking.car_id, car.id)
            # circle reference works
            self.assertTrue(booking in booking.person.booking)
            self.assertTrue(person1 == Booking.query.filter_by(person=person1).first().person)
            self.assertEqual(booking.person.type, person_type1)
            # find all car person1 has booked
            self.assertTrue(car in [b.car for b in person1.booking])


class ValidationTest(TestCase):
    def setUp(self) -> None:
        self.app = get_test_app()

    # for now, only test data that might actually be used by the api for first assignment
    def test_schema_load_data_from_json(self):
        with self.app.app_context():
            person_schema = PersonSchema()
            person = person_schema.loads(DummyPerson.p2_json_no_id)
            self.assertEqual(type(person), Person)

            booking_schema = BookingSchema()
            # deserialize to json string
            booking_json = booking_schema.dumps(DummyBooking.person1_car1_available)
            # serialize from json string
            booking = booking_schema.loads(DummyBooking.b1_json)
            self.assertEqual(type(booking), Booking)

    def test_booking_end_date_before_start_date(self):
        with self.app.app_context():
            schema = BookingSchema(exclude=['id'])
            booking = DummyBooking.person1_car1_available
            booking.start_time = datetime.now() + timedelta(days=100)
            booking.end_time = datetime.now()
            booking_jsonstr = json.dumps(schema.dump(booking))
            with self.assertRaises(ValidationError) as cm:
                schema.loads(booking_jsonstr)
            self.assertEqual(['end_time can not be before start_time'], cm.exception.messages['_schema'])







