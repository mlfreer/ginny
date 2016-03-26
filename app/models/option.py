from app import db
import datetime

class Option(db.Model):
    name = db.Column(db.String(32), primary_key=True)
    value = db.Column(db.String(32), nullable=False)