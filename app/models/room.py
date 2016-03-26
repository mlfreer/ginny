from app import db, cache
from app.models.gamer import Gamer
from app.models.game import Game
from app.models.game_to_stage import GameToStage
from app.models.stage import Stage
from app.models.gamer_action import GamerAction
from app.models.history_variables import HistoryVariables
from sqlalchemy import event, and_
from itertools import groupby
import traceback

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_trial_id = db.Column(db.ForeignKey('game_trial.id'), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    current_step = db.Column(db.Integer, default=0)
    gamers = db.relationship(Gamer,
                             order_by=Gamer.order_number,
                             backref='room',
                             lazy='dynamic')
    finished = db.Column(db.Boolean, nullable=False, server_default="False", default=False, info={'label': 'Finished'})

    @classmethod
    @cache.memoize(3600)
    def get_stage_cls(cls, self, ix):
        return self.game_trial.game.stages[ix]

    @classmethod
    @cache.memoize(3600)
    def get_prepared_actions(cls, room_id, round):
        if round == -1:
            return []
        else:
            actions_by_round = Room.get_prepared_actions(room_id, round - 1)
            room = Room.query.filter(Room.id == room_id).one()
            gamer_actions = GamerAction.query.join(GameToStage,
                                                        and_(GameToStage.stage_id == GamerAction.stage_id,
                                                             GameToStage.game_id == room.game_trial.game_id))\
                    .filter(GamerAction.round == round)\
                    .filter(GamerAction.room_id == room_id)\
                    .order_by(GameToStage.order_number).order_by(GamerAction.gamer_id).all()
            aggregate = {'by_gamer': {}, 'by_action': {}}
            for gamer_action in gamer_actions:
                aggregate['by_gamer'].setdefault(gamer_action.gamer_id, {})
                aggregate['by_gamer'][gamer_action.gamer_id][gamer_action.stage.name] = gamer_action.action
                if gamer_action.stage.clazz == 'options':
                    aggregate['by_action'].setdefault(gamer_action.stage.name, {})
                    for a in gamer_action.stage.options.split(';'):
                        aggregate['by_action'][gamer_action.stage.name].setdefault(a, [])
                    aggregate['by_action'][gamer_action.stage.name][gamer_action.action].append(gamer_action.gamer.id)
            actions_by_round.append(aggregate)
            return actions_by_round

    def get_stage(self, ix):
        return Room.get_stage_cls(self, ix)

    def get_number_of_stages(self):
        return GameToStage.query.filter(GameToStage.game == self.game_trial.game).count()

    def get_current_stage(self):
        return self.get_stage(self.get_current_stage_ix())

    def get_current_stage_ix(self):
        return self.current_step % self.get_number_of_stages()

    def is_last_stage(self):
        return self.get_current_stage_ix() == (self.get_number_of_stages() - 1)

    def get_current_round(self):
        return int(self.current_step / self.get_number_of_stages())

    def get_moved_gamers(self):
        q = Gamer.query\
            .join(Gamer.actions)\
            .filter(GamerAction.room_id == self.id)\
            .filter(GamerAction.round == self.get_current_round())\
            .filter(GamerAction.stage_id == self.get_current_stage().id)\
            .order_by(Gamer.order_number)
        return q.all()

    def get_active_gamers(self):
        left_gamers = [g for g in self.gamers if g not in self.get_moved_gamers()]
        return left_gamers

    def calculate_variables(self):
        if not self.is_last_stage():
            raise RuntimeError('Variables must be calculated at last stage')
        current_round = self.get_current_round()
        game = self.game_trial.game
        actions = Room.get_prepared_actions(self.id, current_round)
        number_of_gamers = self.gamers.count()
        for gamer in self.gamers:
            old_variables = gamer.variables.copy()
            self.move_to_history(gamer, old_variables)
            gamer.variables = game.calculate_variables(old_variables, actions, gamer.id, current_round=current_round, number_of_gamers=number_of_gamers)

    def move_to_history(self, gamer, variables):
        history_variable_record = HistoryVariables(room_id=self.id, round=self.get_current_round(), gamer_id=gamer.id, variables=variables)
        db.session.add(history_variable_record)

    def __init__(self, **kwargs):
        super(Room, self).__init__(**kwargs)

    def is_finished(self):
        return self.finished or self.game_trial.finished