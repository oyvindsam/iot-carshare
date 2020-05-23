from unittest import TestCase

from flask import Flask
from marshmallow import ValidationError

from api.api import api
from api.models import db, PersonSchema, BookingSchema, CarSchema
from api.test.dummy_data import *
from app import create_app

LOCAL = True


def get_production_db_test_app():
    app = create_app()
    #DB_URI = 'mysql://root:carshare@gcloud ip adress/carshare_db_test'
    app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
    return app


def get_test_app():
    if not LOCAL:
        return get_production_db_test_app()

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:?cache=shared'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    db.init_app(app)
    app.register_blueprint(api)
    with app.app_context():
        db.drop_all()
        db.create_all()
    return app


class DatabaseTest(TestCase):

    def setUp(self) -> None:
        self.app = get_test_app()

    def test_add_person_to_db(self):
        with self.app.app_context():
            p1 = DummyPerson.create_random()
            p2 = DummyPerson.create_random()
            db.session.add(p1)
            db.session.add(p2)
            db.session.commit()

            p11 = Person.query.filter_by(username=p1.username).first()
            p22 = Person.query.filter_by(username=p2.username).first()
            self.assertEqual(p1.username, p11.username)
            self.assertTrue(p11.id < p22.id)


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

            # set up persons
            self.person_type1 = add_to_db(DummyPersonType.create_random()).id
            person1 = DummyPerson.create_random()
            person1.person_type = self.person_type1

            self.person1 = add_to_db(person1).id

            # Note: self.type1 is the id (int), not a object.
            self.car_type1 = add_to_db(DummyCarType.create_random()).id
            self.car_type2 = add_to_db(DummyCarType.create_random()).id
            self.manufacturer1 = add_to_db(DummyCarManufacturer.create_random()).id
            self.manufacturer2 = add_to_db(DummyCarManufacturer.create_random()).id
            self.colour1 = add_to_db(DummyCarColour.create_random()).id
            self.colour2 = add_to_db(DummyCarColour.create_random()).id

            car1 = DummyCar.create_random()
            car2 = DummyCar.create_random()
            car3 = DummyCar.create_random()

            car1.car_type = self.car_type1
            car1.car_manufacturer = self.manufacturer1
            car1.car_colour = self.colour1
            car2.car_type = self.car_type1
            car2.car_manufacturer = self.manufacturer1
            car2.car_colour = self.colour1

            car3.car_type = self.car_type1  # Same
            car3.car_colour = self.colour2  # Different than the others
            car3.car_manufacturer = self.manufacturer2  # Different than the others

            # Finally add cars with correct foreign keys
            self.car1 = add_to_db(car1).id
            self.car2 = add_to_db(car2).id
            self.car3 = add_to_db(car3).id

            # booking1 is now + 5 hours
            booking1 = DummyBooking.create_random()
            booking1.car_id = self.car1
            booking1.person_id = self.person1

            # booking 2 is in 1 day
            booking2 = duplicate_db_object(BookingSchema, booking1)
            booking2.car_id = car2.id
            booking2.start_time = datetime.now() + timedelta(days=1)
            booking2.end_time = datetime.now() + timedelta(days=1, hours=5)

            # booking3 was yesterday
            booking3 = duplicate_db_object(BookingSchema, booking1)
            booking3.car_id = car2.id
            booking3.start_time = datetime.now() - timedelta(days=2)
            booking3.end_time = datetime.now() - timedelta(days=1, hours=5)

            self.booking1 = add_to_db(booking1).id
            self.booking2 = add_to_db(booking2).id
            self.booking3 = add_to_db(booking3).id

    # Person tests
    #
    def test_add_person_type(self):
        with self.app.test_client() as app:
            response = app.post('/api/person_type', json=DummyPersonType.pt_customer_no_id_json)
            self.assertEqual(response.status_code, 201)

    # id is automatically added by the db
    def test_cant_add_person_with_id(self):
        with self.app.test_client() as app:
            p1 = DummyPerson.creat_random_json(id=11)
            response_post = app.post('/api/person', json=p1)
            self.assertEqual(400, response_post.status_code)


    def test_add_get_person(self):
        with self.app.test_client() as app:
            p1 = DummyPerson.creat_random_json()
            response_post = app.post('/api/person', json=p1)
            self.assertEqual(response_post.status_code, 201)

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
            person = DummyPerson.creat_random_json()

            response_valid = app.post('/api/person', json=person)
            response_error = app.post('/api/person', json=person)
            self.assertEqual(response_valid.status_code, 201)
            self.assertEqual(response_error.status_code, 409)

    # Booking tests

    def test_add_valid_booking(self):
        with self.app.app_context():
            with self.app.test_client() as app:
                person1 = Person.query.get(self.person1)
                #person2 = add_to_db(duplicate_db_object(PersonSchema, person1))
                # hacky way to make a new booking
                booking1 = Booking.query.get(self.booking1)
                booking2 = duplicate_db_object(BookingSchema, booking1)

                # add car not currently in a booking
                booking2.car_id = self.car2
                #booking2.start_time = datetime.now() + timedelta(hours=1)
                #booking2.person_id = person2

                booking_jsonstr = json.dumps(BookingSchema(exclude=['id', 'status']).dump(booking2))

                response_valid = app.post(f"/api/person/{person1.username}/booking", json=booking_jsonstr)
                self.assertEqual(response_valid.status_code, 201)

    def test_add_booking_with_car_in_use(self):
        with self.app.app_context():
            with self.app.test_client() as app:
                person1 = Person.query.get(self.person1)
                # booking1 already has car 1 in use
                booking2 = duplicate_db_object(BookingSchema, Booking.query.get(self.booking1))

                booking_jsonstr = json.dumps(BookingSchema(exclude=['id', 'status']).dump(booking2))

                # Car is in use, should return error
                response_error = app.post(f"/api/person/{person1.username}/booking", json=booking_jsonstr)
                self.assertEqual(403, response_error.status_code)

    def test_add_invalid_booking_username_gives_error(self):
        with self.app.app_context():
            with self.app.test_client() as app:
                # serialize booking to json str
                booking1 = Booking.query.get(self.booking1)
                person1 = Person.query.get(self.person1)
                booking_jsonstr = json.dumps(BookingSchema(exclude=['id', 'status']).dump(booking1))

                # post to username that does not match booking person username
                response_wrong_username = app.post(
                    f"/api/person/wrongusername/booking", json=booking_jsonstr)
                self.assertEqual(403, response_wrong_username.status_code)


    # This does not work. SQLAclhemy with MySql db will throw IntegrityError: (1452),
    # This needs less strict relationships in ORM, eg. use NULLABLE=True (instead of False)
    # def test_add_booking_invalid_data_gives_error(self):
    #     with self.app.app_context():
    #         with self.app.test_client() as app:
    #             # serialize booking to json str
    #             booking1 = Booking.query.get(self.booking1)
    #             person1 = Person.query.get(self.person1)
    #
    #             # give valid data that does not match db
    #             booking1.car_id = -1
    #             booking_jsonstr = json.dumps(BookingSchema(exclude=['id']).dump(booking1))
    #             response_invalid_data = app.post(f"/api/person/{person1.username}/booking", json=booking_jsonstr)
    #             self.assertEqual(403, response_invalid_data.status_code)
    #
    #             # give invalid data (missing car id)
    #             booking_jsonstr = json.dumps({
    #                 'car_id': '',
    #                 'person_id': 1,
    #                 'start_time': '2020-05-03T21:2',
    #                 'end_time': '2020-05-04T02:2',
    #                 'status_id': 1
    #             })
    #             response_invalid_data = app.post(f"/api/person/{person1.username}/booking",json=booking_jsonstr)
    #             self.assertEqual(400, response_invalid_data.status_code)

    def test_get_valid_booking(self):
        with self.app.app_context():
            with self.app.test_client() as app:
                # serialize booking to json str
                booking1 = Booking.query.get(self.booking1)
                person1 = Person.query.get(self.person1)

                booking_jsonstr = json.dumps(BookingSchema(exclude=['id', 'status']).dump(booking1))

                response_get = app.get(
                    f'/api/person/{person1.username}/booking')
                self.assertEqual(response_get.status_code, 200)

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
                car1 = Car.query.get(self.car1)

                car4 = DummyCar.create_random()
                car4.car_colour = self.colour1
                car4.car_manufacturer = self.manufacturer1
                add_to_db(car4)
                filters = {
                    'car_colour': colour1.id,
                    'car_manufacturer': manufacturer1.id
                }
                response = app.get('/api/car', query_string=filters)
                self.assertEqual(200, response.status_code)

                response_cars = CarSchema(many=True).loads(response.get_json())
                self.assertTrue(type(Car), type(response_cars[0]))
                self.assertTrue(all([car.car_colour == self.colour1 for car in response_cars]))
                self.assertFalse(car1 in response_cars)
                self.assertTrue(car4.id in [c.id for c in response_cars])

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

    def test_form_post_get_filtered_cars(self):
        with self.app.app_context():
            with self.app.test_client() as app:
                colour1 = CarColour.query.get(self.colour1)
                manufacturer1 = CarManufacturer.query.get(self.manufacturer1)
                car1 = Car.query.get(self.car1)

                car4 = DummyCar.create_random()
                car4.car_colour = self.colour1
                car4.car_manufacturer = self.manufacturer1
                add_to_db(car4)
                filters = {
                    'car_colour': colour1.id,
                    'car_manufacturer': manufacturer1.id
                }
                response = app.post('/api/car', data=filters)
                self.assertEqual(200, response.status_code)

                response_cars = CarSchema(many=True).loads(response.get_json())
                self.assertTrue(type(Car), type(response_cars[0]))
                self.assertTrue(all([car.car_colour == self.colour1 for car in response_cars]))
                self.assertFalse(car1 in response_cars)
                self.assertTrue(car4.id in [c.id for c in response_cars])

    def test_update_car_location(self):
        with self.app.app_context():
            with self.app.test_client() as app:
                car = Car.query.get(self.car1)
                lat = '123.321'
                long = '321.123'
                data = {
                    'latitude': lat,
                    'longitude': long
                }
                response = app.put(f'api/car/{car.id}/location', data=data)
                response_car = CarSchema().loads(response.get_json())
                self.assertEqual(200, response.status_code)
                self.assertEqual(lat, response_car.latitude)
                self.assertEqual(long, response_car.longitude)
                self.assertEqual(lat, car.latitude)

    def test_update_car_location_with_bad_data_return_error(self):
        with self.app.app_context():
            with self.app.test_client() as app:
                car = Car.query.get(self.car1)
                lat = 'this is not a float string'
                long = '321.123'
                data = {
                    'latitude': lat,
                    'longitude': long
                }
                response = app.put(f'api/car/{car.id}/location', data=data)
                self.assertEqual(400, response.status_code)

    def test_update_missing_car(self):
        with self.app.app_context():
            with self.app.test_client() as app:
                car = Car.query.get(self.car1)
                lat = '123.321'
                long = '321.123'
                data = {
                    'latitude': lat,
                    'longitude': long
                }
                response = app.put(f'api/car/948483/location', data=data)
                self.assertEqual(404, response.status_code)

    def test_get_booking_for_person(self):
        with self.app.app_context():
            with self.app.test_client() as app:
                person1 = Person.query.get(self.person1)
                booking1 = Booking.query.get(self.booking1)
                response = app.get(f'api/person/{person1.username}/booking/{booking1.id}')
                self.assertEqual(200, response.status_code)
                data = response.get_json()
                booking = BookingSchema().loads(data['booking'])
                person = PersonSchema().loads(data['person'])
                car = CarSchema().loads(data['car'])
                self.assertEqual(type(booking1), type(booking))

    def test_get_bookings_for_person(self):
        with self.app.app_context():
            with self.app.test_client() as app:
                person1 = Person.query.get(self.person1)
                booking1 = Booking.query.get(self.booking1)
                car1 = Car.query.get(self.car1)
                response = app.get(f'api/person/{person1.username}/booking')
                self.assertEqual(200, response.status_code)
                data = response.get_json()
                self.assertIsNotNone(data)
                for booking_info in data:
                    self.assertEqual(type(booking1), type(BookingSchema().loads(booking_info['booking'])))
                    self.assertEqual(type(person1), type(PersonSchema().loads(booking_info['person'])))
                    self.assertEqual(type(car1), type(CarSchema().loads(booking_info['car'])))


def add_to_db(thing):
    """
    Helper method to add things to db and return object
    Args:
        thing: SQLAlchemy object

    Returns: SQLAlchemy object with id generated from db

    """
    db.session.add(thing)
    db.session.commit()
    return thing


def duplicate_db_object(schema, db_object):
    """
    Helper method to generate a duplicate of a db object, with new id.
    Args:
        schema: Marshmallow schema for object
        db_object: SQLAlchemy object from db

    Returns: New SQLAlchemy object (not added to db -> no id)

    """
    obj_dict = schema().dump(db_object)
    del(obj_dict['id'])
    return schema().load(obj_dict)


class ModelTest(TestCase):
    def setUp(self) -> None:
        self.app = get_test_app()

        with self.app.app_context():

            # set up persons
            self.person_type1 = add_to_db(DummyPersonType.create_random()).id
            person1 = DummyPerson.create_random()
            person1.person_type = self.person_type1

            self.person1 = add_to_db(person1).id

            # Note: self.type1 is the id (int), not a object.
            self.car_type1 = add_to_db(DummyCarType.create_random()).id
            self.car_type2 = add_to_db(DummyCarType.create_random()).id
            self.manufacturer1 = add_to_db(DummyCarManufacturer.create_random()).id
            self.manufacturer2 = add_to_db(DummyCarManufacturer.create_random()).id
            self.colour1 = add_to_db(DummyCarColour.create_random()).id
            self.colour2 = add_to_db(DummyCarColour.create_random()).id

            car1 = DummyCar.create_random()
            car2 = DummyCar.create_random()
            car3 = DummyCar.create_random()

            car1.car_type = self.car_type1
            car1.car_manufacturer = self.manufacturer1
            car1.car_colour = self.colour1
            car2.car_type = self.car_type1
            car2.car_manufacturer = self.manufacturer1
            car2.car_colour = self.colour1

            car3.car_type = self.car_type1  # Same
            car3.car_colour = self.colour2  # Different than the others
            car3.car_manufacturer = self.manufacturer2  # Different than the others

            # Finally add cars with correct foreign keys
            self.car1 = add_to_db(car1).id
            self.car2 = add_to_db(car2).id
            self.car3 = add_to_db(car3).id

            # booking1 is now + 5 hours
            booking1 = DummyBooking.create_random()
            booking1.car_id = self.car1
            booking1.person_id = self.person1

            # booking 2 is in 1 day
            booking2 = duplicate_db_object(BookingSchema, booking1)
            booking2.car_id = car2.id
            booking2.start_time = datetime.now() + timedelta(days=1)
            booking2.end_time = datetime.now() + timedelta(days=1, hours=5)

            # booking3 was yesterday
            booking3 = duplicate_db_object(BookingSchema, booking1)
            booking3.car_id = car2.id
            booking3.start_time = datetime.now() - timedelta(days=2)
            booking3.end_time = datetime.now() - timedelta(days=1, hours=5)

            self.booking1 = add_to_db(booking1).id
            self.booking2 = add_to_db(booking2).id
            self.booking3 = add_to_db(booking3).id


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
            booking.car_id = car.id
            booking.person_id = person1.id

            self.assertEqual(booking.car_id, car.id)
            # circle reference works
            self.assertTrue(booking in booking.person.booking)
            self.assertTrue(person1 == Booking.query.filter_by(person=person1).first().person)
            self.assertEqual(booking.person.type, person_type1)
            # find all car person1 has booked
            self.assertTrue(car in [b.car for b in person1.booking])

    def test_is_car_busy(self):
        with self.app.app_context():
            b1 = Booking.query.get(self.booking1)
            b1.start_time = datetime.now() + timedelta(days=50)
            b1.end_time = datetime.now() + timedelta(days=50, hours=10)
            b2 = duplicate_db_object(BookingSchema, b1)

            # b2 want to start before b1
            b2.start_time = b1.start_time - timedelta(hours=1)

            # Car should be busy since b1 will be using it in the requested time
            self.assertTrue(Booking.is_car_busy(b2.start_time, b2.end_time, b2.car_id))

            # New booking 3
            b3 = duplicate_db_object(BookingSchema, b1)
            b3.start_time = b1.start_time + timedelta(days=1)
            b3.end_time = b1.end_time + timedelta(days=1)

            # Car should _not_ be busy since b1 is outside the requested time
            self.assertFalse(Booking.is_car_busy(b3.start_time, b3.end_time, b3.car_id))

            # Check booking 2 with updated booking1 status
            b1.status = BookingStatusEnum.FINISHED
            # Now it should not be active since b1 finished his booking
            self.assertFalse(Booking.is_car_busy(b2.start_time, b2.end_time, b2.car_id))



class ValidationTest(TestCase):
    def setUp(self) -> None:
        self.app = get_test_app()

    # for now, only test data that might actually be used by the api for first assignment
    def test_schema_load_data_from_json(self):
        with self.app.app_context():
            person_schema = PersonSchema()
            person = person_schema.loads(DummyPerson.creat_random_json(id=None))
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







