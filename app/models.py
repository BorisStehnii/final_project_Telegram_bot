
from app import db


class client_wm(db.Model):

    __tablename__ = 'client_wm'

    client_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String, nullable=True)
    address = db.Column(db.String)
    phone = db.Column(db.String)
    brand = db.Column(db.String)
    breaking = db.Column(db.String)
    repair = db.Column(db.String)
    invoice = db.Column(db.Integer)
    cost = db.Column(db.Integer)
    profit = db.Column(db.Integer)
    debt = db.Column(db.String)

