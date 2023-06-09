from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Stocks(db.Model):
    __tablename__ = 'stockdetails'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
