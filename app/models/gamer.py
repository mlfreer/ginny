from app import db
from app.models.history_variables import HistoryVariables
from flask_security.core import UserMixin
from sqlalchemy.dialects.postgresql import HSTORE
from sqlalchemy.ext.mutable import MutableDict

class Gamer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    game_trial_id = db.Column(db.Integer, db.ForeignKey('game_trial.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    order_number = db.Column(db.Integer)
    variables = db.Column(MutableDict.as_mutable(HSTORE), index=True)
    show_results = db.Column(db.Boolean)
    shown_results = db.Column(db.Boolean)

    def get_show_variables(self):
        if self.room_id is None:
            raise RuntimeError("Game trial hasn't been started.")
        game = self.game_trial.game
        room = self.room
        current_round = room.get_current_round()
        actions = room.get_prepared_actions(room.id, current_round - 1)
        history_variables = HistoryVariables.query.filter(HistoryVariables.room_id == room.id,
                                                          HistoryVariables.round == current_round - 1,
                                                          HistoryVariables.gamer_id == self.id).order_by(HistoryVariables.round).one().variables
        return game.show_variables(history_variables, self.variables, actions, round=current_round - 1)

    def is_active(self):
        return True

    def get_id(self):
        return 'g_' + str(self.id)

    def has_role(self, role):
        return role == 'gamer'

    def __repr__(self):
        return '<Gamer %r>' % (self.id)
