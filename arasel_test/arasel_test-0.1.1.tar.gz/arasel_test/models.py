from sqlalchemy import String, Column, Float

from arasel_test import db

class Customer(db.Model):
    __tablename__ = 'customers'

    customer_id = Column(String, primary_key=True)
    clv = Column(Float)
