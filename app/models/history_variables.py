from app import db
from flask_security.core import UserMixin
from sqlalchemy.dialects.postgresql import HSTORE
from sqlalchemy.ext.mutable import MutableDict

class HistoryVariables(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), index=True)
    gamer_id = db.Column(db.Integer, db.ForeignKey('gamer.id'), index=True)
    round = db.Column(db.Integer, index=True)
    variables = db.Column(MutableDict.as_mutable(HSTORE), index=True)