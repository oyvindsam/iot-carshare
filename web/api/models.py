from datetime import datetime

from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from marshmallow import post_load, validate, ValidationError, \
    validates_schema, fields
from marshmallow_sqlalchemy import auto_field
from sqlalchemy import or_
from sqlalchemy.orm import backref

db = SQLAlchemy()
ma = Marshmallow()


class PersonType:
    CUSTOMER = 'CUSTOMER'
    ADMIN = 'ADMIN'
    MANAGER = 'MANAGER'
    ENGINEER = 'ENGINEER'

    ALL = [
        CUSTOMER,
        ADMIN,
        MANAGER,
        ENGINEER,
    ]


class Person(db.Model):
    """
    Person SQLAlchemy class
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(40), nullable=False)
    last_name = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(40), nullable=False)
    type = db.Column(db.String(20), nullable=False, default=PersonType.CUSTOMER)
    password = db.Column(db.String(200), nullable=False)
    face = db.Column(db.BLOB)


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
    hour_rate = db.Column(db.Float(6), nullable=False)
    manufacturer = db.relationship('CarManufacturer', backref='car', lazy=True)
    color = db.relationship('CarColour', backref='car', lazy=True)
    type = db.relationship('CarType', backref='car', lazy=True)


class CarIssue(db.Model):
    """
    CarIssue SQLAlchemy class
    """
    id = db.Column(db.Integer, primary_key=True)
    issue = db.Column(db.Text, nullable=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=True)
    car = db.relationship('Car', backref=backref('issue', uselist=False), lazy=True)


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


# Marshmallow does not support Enum, use String. In future: look at marshmallow-enum
class BookingStatusEnum:
    NOT_ACTIVATED = 'Not active'
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
    status = db.Column(db.String(20), default=BookingStatusEnum.NOT_ACTIVATED)
    google_calendar_id = db.Column(db.String(200), nullable=True)

    # Is a car available if it is after end_time, but user has _not_ returned it yet?.. no
    # Or before end_time and user _has_ returned it. This argues for hard coded statuses
    @classmethod
    def filter_by_is_active(cls):
        time = datetime.now()
        return Booking.query.filter(
            Booking.start_time < time,
            Booking.end_time > time)

    @classmethod
    def is_car_busy(cls, start_time: datetime, end_time: datetime, car_id: int) -> bool:
        """
        Check if an active booking within this time period uses this car
        Args:
            start_time (datetime):
            end_time (datetime):
            car_id (int):

        Returns: bool if car is in use

        """
        results = Booking.query \
            .filter(Booking.car_id == car_id) \
            .filter((start_time <= Booking.start_time) & (Booking.start_time <= end_time)  |
                    (Booking.start_time < start_time) & (start_time <= Booking.end_time) |
                    (start_time <= Booking.end_time) & (Booking.end_time <= end_time) |
                    (start_time < Booking.start_time) & (Booking.end_time < end_time)) \
            .filter(Booking.status == BookingStatusEnum.ACTIVE).count()

        return results > 0

def is_active(self):
    return self.start_time < datetime.now() < self.end_time


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


class CarIssueSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CarIssue
        include_fk = True

    @post_load
    def make_issue(self, data, **kwargs):
        """
        This function runs after Schema().loads (validation code).

        Args:
            data: Valid data
            **kwargs: args passed automatically

        Returns:

        """
        return CarIssue(**data)


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

    start_time = fields.DateTime("%Y-%m-%d %H:%M:%S")
    end_time = fields.DateTime("%Y-%m-%d %H:%M:%S")

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
