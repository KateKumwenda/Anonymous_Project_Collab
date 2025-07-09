# models/tip.py
from extensions import db
from datetime import datetime


class Tip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    corruption_type = db.Column(db.String(100), nullable=False)
    location= db.Column(db.String(100))
    date= db.Column(db.String(20))
    people = db.Column(db.String(200))
    tip_category= db.Column(db.String(100))
    text = db.Column(db.Text)
    file = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
