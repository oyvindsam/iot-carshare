from datetime import datetime
from enum import Enum

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import post_load, validate, fields, ValidationError, \
    validates_schema
from marshmallow_sqlalchemy import auto_field

db = SQLAlchemy()
ma = Marshmallow()


class Person(db.Model):
    """
    Person SQLAlchemy class
    """
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
    """
    PersonType SQLAlchemy class
    """
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(40), nullable=False, unique=True)


class Car(db.Model):
    """
    Car SQLAlchemy class
    """
    id = db.Column(db.Integer, primary_key=True)
    reg_number = db.Column(db.String(6), nullable=False, unique=True)
    car_manufacturer = db.Column(db.Integer,
                                 db.ForeignKey('car_manufacturer.id'), nullable=False)
    car_colour = db.Column(db.Integer, db.ForeignKey('car_colour.id'), nullable=False)
    car_type = db.Column(db.Integer, db.ForeignKey('car_type.id'), nullable=False)
    seats = db.Column(db.Integer, nullable=False)
    latitude = db.Column(db.String(20))
    longitude = db.Column(db.String(20))
    #hour_rate = db.Column(db.DECIMAL(5, 2), nullable=False)
    hour_rate = db.Column(db.Float(6), nullable=False)
    manufacturer = db.relationship('CarManufacturer', backref='car', lazy=True)
    color = db.relationship('CarColour', backref='car', lazy=True)
    type = db.relationship('CarType', backref='car', lazy=True)


class CarManufacturer(db.Model):
    """
    CarManufacturer SQLAlchemy class
    """
    id = db.Column(db.Integer, primary_key=True)
    manufacturer = db.Column(db.String(20), nullable=False, unique=True)


class CarType(db.Model):
    """
    CarType SQLAlchemy class
    """
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False, unique=True)


class CarColour(db.Model):
    """
    CarColour SQLAlchemy class
    """
    id = db.Column(db.Integer, primary_key=True)
    colour = db.Column(db.String(20), nullable=False, unique=True)


class BookingStatus(Enum):
    ACTIVE = 'Active'
    FINISHED = 'Finished'
    CANCELLED = 'Cancelled'


class Booking(db.Model):
    """
    Booking SQLAlchemy class
    """
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    car = db.relationship('Car', backref='booking', lazy=True)
    person = db.relationship('Person', backref='booking', lazy=True)
    status = db.Column(db.String(20), default=BookingStatus.ACTIVE, nullable=False)
    #status_id = db.Column(db.Integer, db.ForeignKey('booking_status.id'), nullable=False)
    #status = db.relationship('BookingStatus', backref='booking', lazy=True)

    # Is a car available if it is after end_time, but user has _not_ returned it yet?.. no
    # Or before end_time and user _has_ returned it. This argues for hard coded statuses
    @classmethod
    def filter_by_is_active(cls):
        time = datetime.now()
        return Booking.query.filter(
            Booking.start_time < time,
            Booking.end_time > time)

    def is_active(self):
        return self.start_time < datetime.now() < self.end_time


# TODO: This might be redundant by above code..
# FIXME: Only have hardcoded AVAILABLE / UNAVAILABLE statuses?
# Is a car available if it is after end_time, but user has not returned it yet?.. no
# class BookingStatus(db.Model):
#     """
#     BookingStatus SQLAlchemy class
#     """
#     id = db.Column(db.Integer, primary_key=True)
#     status = db.Column(db.String(20), nullable=False, unique=True)


not_blank = validate.Length(min=1, error='Field cannot be blank')


class PersonSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        """
        Attributes:
            include_fk (bool): When validating we want all foreign keys
                to be present.
        """
        model = Person
        include_fk = True

    first_name = auto_field(validate=not_blank)

    @post_load
    def make_person(self, data, **kwargs):
        """
        This function runs after Schema().loads (validation code).

        Args:
            data: Valid data

        Returns: Person

        """
        return Person(**data)


class PersonTypeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PersonType

    @post_load
    def make_person_type(self, data, **kwargs):
        """
        This function runs after Schema().loads (validation code).

        Args:
            data: Valid data
            **kwargs: args passed automatically

        Returns:

        """
        return PersonType(**data)


class CarSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Car
        include_fk = True

    @post_load
    def make_car(self, data, **kwargs):
        """
        This function runs after Schema().loads (validation code).

        Args:
            data: Valid data
            **kwargs: args passed automatically

        Returns:

        """
        return Car(**data)


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
        """
        This function runs after Schema().loads (validation code).

        Args:
            data: Valid data
            **kwargs: args passed automatically

        Returns:

        """
        return Booking(**data)

    @validates_schema
    def validate_dates(self, data, **kwargs):
        if data['end_time'] < data['start_time']:
            raise ValidationError('end_time can not be before start_time')


class BookingStatusSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BookingStatus

    @post_load
    def make_booking_status(self, data, **kwargs):
        """
        This function runs after Schema().loads (validation code).

        Args:
            data: Valid data
            **kwargs: args passed automatically

        Returns:

        """
        return BookingStatus(**data)
