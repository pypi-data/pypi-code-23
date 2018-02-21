import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import generic_relationship


@as_declarative()
class Base:
    pass


engine = create_engine("sqlite:///test.db")
session = sessionmaker(bind=engine)()


class User(Base):
    __tablename__ = 'user'
    id = sa.Column(sa.Integer, primary_key=True)


class Customer(Base):
    __tablename__ = 'customer'
    id = sa.Column(sa.Integer, primary_key=True)


class Event(Base):
    __tablename__ = 'event'
    id = sa.Column(sa.Integer, primary_key=True)

    # This is used to discriminate between the linked tables.
    object_type = sa.Column(sa.Unicode(255))

    # This is used to point to the primary key of the linked row.
    object_id = sa.Column(sa.Integer)

    object = generic_relationship(object_type, object_id,
                                  map_type2discriminator={"User": "U1",
                                                          "Customer": "C2",
                                                          }
                                  )


# Base.metadata.create_all(engine)

if False:
    # Some general usage to attach an event to a user.
    user = User()
    customer = Customer()

    session.add_all([user, customer])
    session.commit()

    ev = Event()
    ev.object = customer

    session.add(ev)
    session.commit()
else:
    customer = session.query(Customer).all()[0]
    user = session.query(User).all()[0]

    ev = session.query(Event).all()[0]

# Find the event we just made.
print(ev.object)

# ev.object = customer
# print(ev.object)
# session.commit()
# print(ev.object)

# Find any events that are bound to users.
for ev in session.query(Event).all():
    print("-",ev, ev.object)

for ev in session.query(Event).filter(Event.object.is_type(User)).all():
    print("o", ev, ev.object)

for ev in session.query(Event).filter_by(object=user).all():
    print("x", ev, ev.object)
