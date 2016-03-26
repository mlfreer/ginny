from app import db
from app.models import Game

class GameToStage(db.Model):
    game_id = db.Column(db.ForeignKey('game.id'), primary_key=True)
    stage_id = db.Column(db.ForeignKey('stage.id'), primary_key=True)
    order_number = db.Column(db.Integer)
    game = db.relationship('Game', backref=db.backref('game_to_stage'))
    stage = db.relationship('Stage', backref=db.backref('game_to_stage'))