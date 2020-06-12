from unittest import TestCase

import matplotlib.pyplot as plt

from api.models import BookingSchema
from api.test.dummy_data import *
from api.test.tests import get_test_app, add_to_db, duplicate_db_object


class StatisticsTest(TestCase):
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
            person1 = DummyPerson.create_random()

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
            booking1.start_time = datetime.now()
            booking1.end_time = datetime.now() + timedelta(days=0, hours=5)

            # booking 2 is in 1 day
            booking2 = duplicate_db_object(BookingSchema, booking1)
            booking2.car_id = car2.id
            booking2.start_time = datetime.now() + timedelta(days=1)
            booking2.end_time = datetime.now() + timedelta(days=4, hours=5)

            booking3 = duplicate_db_object(BookingSchema, booking1)
            booking3.car_id = car2.id
            booking3.start_time = datetime.now() - timedelta(days=3)
            booking3.end_time = datetime.now() - timedelta(days=2, hours=10)

            # booking3 was yesterday
            booking4 = duplicate_db_object(BookingSchema, booking1)
            booking4.car_id = car2.id
            booking4.start_time = datetime.now()
            booking4.end_time = datetime.now() + timedelta(days=2, hours=1)

            booking5 = duplicate_db_object(BookingSchema, booking1)
            booking5.car_id = car2.id
            booking5.start_time = datetime.now() - timedelta(days=6)
            booking5.end_time = datetime.now() - timedelta(days=4, hours=5)

            booking6 = duplicate_db_object(BookingSchema, booking1)
            booking6.car_id = car2.id
            booking6.start_time = datetime.now() - timedelta(days=5)
            booking6.end_time = datetime.now() - timedelta(days=4, hours=5)

            #self.booking1 = add_to_db(booking1).id
            ##self.booking2 = add_to_db(booking2).id
            ##self.booking3 = add_to_db(booking3).id
            ##self.booking4 = add_to_db(booking4).id
            ##self.booking5 = add_to_db(booking5).id
            self.booking6 = add_to_db(booking6).id

    def test_car_usage(self):
        with self.app.app_context():
            with self.app.test_client() as app:
                bookings = filter(
                    lambda b: (b.start_time > datetime.now() - timedelta(
                        weeks=1)) &
                              (b.start_time < datetime.now()),
                    Booking.query.all())
                bookings = [b for b in bookings]
                xs = [datetime.now().replace(hour=0, minute=0) - timedelta(days=x) for x in
                      range(7, 0, -1)]  # hours in a week
                print(xs)
                ys = []
                for day in xs:
                    day_count = 0
                    end = day + timedelta(days=1)

                    for b in bookings:
                        print(b.start_time)
                        if (b.start_time < day < b.end_time) \
                                | (day < b.start_time < end) \
                                | (day < b.start_time < end):
                            day_count += 1
                    ys.append(day_count)
                print(ys)
                xs = [x.strftime('%d-%m-%y') for x in xs]

                fig, ax = plt.subplots()

                plt.plot(xs, ys)
                plt.xlabel('Date')
                plt.ylabel('Active rentals')
                plt.title('Active rentals per day for last 7 days')
                plt.show()



