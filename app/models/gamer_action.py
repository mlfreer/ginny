from app import db
import datetime

class GamerAction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gamer_id = db.Column(db.Integer, db.ForeignKey('gamer.id'), nullable=False, index=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False, index=True)
    stage_id = db.Column(db.Integer, db.ForeignKey('stage.id'), nullable=False, index=True)
    round = db.Column(db.Integer, nullable=False, index=True)
    action = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime,
                           default=datetime.datetime.utcnow,
                           nullable=False)

    gamer = db.relationship('Gamer', backref=db.backref('actions', cascade="save-update, merge, delete", lazy='dynamic'))
    room = db.relationship('Room', backref=db.backref('gamer_actions', cascade="save-update, merge, delete"))
    stage = db.relationship('Stage')