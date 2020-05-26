from flask import Flask

from api.models import Person, CarManufacturer, CarType, CarColour, Car, db, \
    PersonType

pt1 = PersonType(
    type='Customer'
)


cm1 = CarManufacturer(
    manufacturer='BMW'
)

cm2 = CarManufacturer(
    manufacturer='Volvo'
)

cm3 = CarManufacturer(
    manufacturer='Volkswagen'
)

ct1 = CarType(
    type='Suv'
)

ct2 = CarType(
    type='Sedan'
)

cc1 = CarColour(
    colour='White'
)

cc2 = CarColour(
    colour='Black'
)

cc3 = CarColour(
    colour='Red'
)


def setup_clean_db():
    print('Updating db...')
    app = Flask(__name__)
    HOST = "34.71.196.78"
    USER = "root"
    PASSWORD = "root1234"
    DATABASE = "hireCar"

    app.config[
        "SQLALCHEMY_DATABASE_URI"] = f"mysql://{USER}:{PASSWORD}@{HOST}/{DATABASE}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.drop_all()
        print('db dropped')
        db.create_all()
        db.session.add_all([
            pt1,
            cm1,
            cm2,
            cm3,
            ct1,
            ct2,
            cc1,
            cc2,
            cc3,
        ])
        db.session.commit()

        p1 = Person(
            username='adi',
            first_name='Adi',
            last_name='Lastname',
            email='raj@gmail.com',
            person_type=pt1.id,
            password_hashed='$5$rounds=535000$PMY9ZLpI5VgtQcUs$0XqCn3u7tZaLTDvoYCHoYtAq5TBRprNQwEwndUZS/M3',
            face=None
        )

        c1 = Car(
            reg_number='abc123',
            car_manufacturer=cm1.id,
            car_type=ct1.id,
            car_colour=cc1.id,
            seats=4,
            latitude='-37.8182711',
            longitude='144.9670618',
            hour_rate=290.5,
        )

        c2 = Car(
            reg_number='bbc123',
            car_manufacturer=cm2.id,
            car_type=ct1.id,
            car_colour=cc1.id,
            seats=4,
            latitude='-37.8',
            longitude='144.96667',
            hour_rate=20.5,
        )

        c3 = Car(
            reg_number='cbc123',
            car_manufacturer=cm1.id,
            car_type=ct2.id,
            car_colour=cc1.id,
            seats=4,
            latitude='-38.21792',
            longitude='145.03876',
            hour_rate=12.5,
        )

        c4 = Car(
            reg_number='dbc123',
            car_manufacturer=cm3.id,
            car_type=ct1.id,
            car_colour=cc1.id,
            seats=4,
            latitude='-37.98333',
            longitude='145.2',
            hour_rate=25.5,
        )

        c5 = Car(
            reg_number='ebc123',
            car_manufacturer=cm3.id,
            car_type=ct1.id,
            car_colour=cc1.id,
            seats=4,
            latitude='-37.7983459',
            longitude='144.960974',
            hour_rate=20.5,
        )

        c6 = Car(
            reg_number='fbc123',
            car_manufacturer=cm3.id,
            car_type=ct1.id,
            car_colour=cc1.id,
            seats=4,
            latitude='-37.829',
            longitude='144.957',
            hour_rate=27.5,
        )

        c7 = Car(
            reg_number='gbc123',
            car_manufacturer=cm3.id,
            car_type=ct1.id,
            car_colour=cc2.id,
            seats=4,
            latitude='-37.8081201',
            longitude='144.9644196',
            hour_rate=11.5,
        )

        c8 = Car(
            reg_number='hbc123',
            car_manufacturer=cm3.id,
            car_type=ct1.id,
            car_colour=cc2.id,
            seats=4,
            latitude='-37.6690123',
            longitude='144.8410273',
            hour_rate=99.5,
        )

        c9 = Car(
            reg_number='ibc123',
            car_manufacturer=cm1.id,
            car_type=ct1.id,
            car_colour=cc2.id,
            seats=4,
            latitude='-37.8332233',
            longitude='144.9124697',
            hour_rate=30.5,
        )

        c10 = Car(
            reg_number='jbc123',
            car_manufacturer=cm1.id,
            car_type=ct1.id,
            car_colour=cc2.id,
            seats=4,
            latitude='59.9139',
            longitude='10.7522',
            hour_rate=70.5,
        )

        c11 = Car(
            reg_number='kbc123',
            car_manufacturer=cm1.id,
            car_type=ct1.id,
            car_colour=cc2.id,
            seats=4,
            latitude='-37.7923459',
            longitude='144.960974',
            hour_rate=20.5,
        )

        c12 = Car(
            reg_number='lbc123',
            car_manufacturer=cm3.id,
            car_type=ct1.id,
            car_colour=cc2.id,
            seats=4,
            latitude='-37.8678765',
            longitude='144.9740049',
            hour_rate=20.5,
        )

        c13 = Car(
            reg_number='mbc123',
            car_manufacturer=cm3.id,
            car_type=ct1.id,
            car_colour=cc1.id,
            seats=4,
            latitude='-38.21792',
            longitude='144.960974',
            hour_rate=50.5,
        )

        c14 = Car(
            reg_number='nbc123',
            car_manufacturer=cm3.id,
            car_type=ct1.id,
            car_colour=cc1.id,
            seats=4,
            latitude='-37.7983459',
            longitude='144.960974',
            hour_rate=20.5,
        )

        c15 = Car(
            reg_number='obc123',
            car_manufacturer=cm3.id,
            car_type=ct1.id,
            car_colour=cc1.id,
            seats=4,
            latitude='37.7983459',
            longitude='144.320974',
            hour_rate=20.5,
        )

        c16 = Car(
            reg_number='pbc123',
            car_manufacturer=cm3.id,
            car_type=ct1.id,
            car_colour=cc1.id,
            seats=4,
            latitude='59.9139',
            longitude='144.110974',
            hour_rate=20.5,
        )

        c17 = Car(
            reg_number='qbc123',
            car_manufacturer=cm3.id,
            car_type=ct2.id,
            car_colour=cc1.id,
            seats=4,
            latitude='37.7183459',
            longitude='144.230974',
            hour_rate=20.5,
        )

        c18 = Car(
            reg_number='rbc123',
            car_manufacturer=cm3.id,
            car_type=ct2.id,
            car_colour=cc1.id,
            seats=4,
            latitude='-37.3983459',
            longitude='144.460974',
            hour_rate=20.5,
        )

        c19 = Car(
            reg_number='sbc123',
            car_manufacturer=cm1.id,
            car_type=ct2.id,
            car_colour=cc1.id,
            seats=4,
            latitude='-37.283459',
            longitude='144.990974',
            hour_rate=20.5,
        )

        c20 = Car(
            reg_number='tbc123',
            car_manufacturer=cm1.id,
            car_type=ct2.id,
            car_colour=cc1.id,
            seats=4,
            latitude='-37.829',
            longitude='144.930974',
            hour_rate=20.5,
        )

        db.session.add_all([
            p1,
            c1,
            c2,
            c3,
            c4,
            c5,
            c6,
            c7,
            c8,
            c9,
            c10,
            c11,
            c12,
            c13,
            c14,
            c15,
            c16,
            c17,
            c18,
            c19,
            c20
        ])
        db.session.commit()
print('___')

setup_clean_db()
