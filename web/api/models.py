from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import post_load, validate, fields
from marshmallow_sqlalchemy import auto_field

db = SQLAlchemy()
ma = Marshmallow()


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(40), nullable=False)
    last_name = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(40), nullable=False)
    person_type = db.Column(db.Integer, db.ForeignKey('person_type.id'),
                            nullable=False)
    password_hashed = db.Column(db.String(80), nullable=False)
    face = db.Column(db.BLOB)
    type = db.relationship('PersonType', backref='person', lazy=True)


class PersonType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(40), nullable=False, unique=True)


class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_number = db.Column(db.String(6), nullable=False, unique=True)
    car_manufacturer = db.Column(db.Integer,
                                 db.ForeignKey('car_manufacturer.id'), nullable=False)
    car_colour = db.Column(db.Integer, db.ForeignKey('car_colour.id'), nullable=False)
    car_type = db.Column(db.Integer, db.ForeignKey('car_type.id'), nullable=False)
    seats = db.Column(db.Integer, nullable=False)
    latitude = db.Column(db.String(20))
    longitude = db.Column(db.String(20))
    hour_rate = db.Column(db.DECIMAL(5, 2), nullable=False)
    manufacturer = db.relationship('CarManufacturer', backref='car', lazy=True)
    color = db.relationship('CarColour', backref='car', lazy=True)
    type = db.relationship('CarType', backref='car', lazy=True)


class CarManufacturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    manufacturer = db.Column(db.String(20), nullable=False, unique=True)


class CarType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False, unique=True)


class CarColour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    colour = db.Column(db.String(20), nullable=False, unique=True)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    booking_status = db.Column(db.Integer, db.ForeignKey('booking_status.id'),
                               nullable=False)
    car = db.relationship('Car', backref='booking', lazy=True)
    person = db.relationship('Person', backref='booking', lazy=True)
    status = db.relationship('BookingStatus', backref='booking', lazy=True)


class BookingStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), nullable=False, unique=True)


not_blank = validate.Length(min=1, error='Field cannot be blank')


class PersonSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Person
        include_fk = True

    first_name = auto_field(validate=not_blank)

    # return an actual Person instance after loading json data
    @post_load
    def make_person(self, data, **kwargs):
        return Person(**data)


class PersonTypeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PersonType

    @post_load
    def make_person_type(self, data, **kwargs):
        return PersonType(**data)


class CarSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Car


class CarManufacturerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CarManufacturer


class CarTypeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CarType


class CarColourSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CarColour


class BookingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Booking
        include_fk = True

    @post_load
    def make_booking(self, data, **kwargs):
        return Booking(**data)


class BookingStatusSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BookingStatus
