import random
from app import db, utils, cache, utils
from sqlalchemy import event

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64),
                      unique=True,
                      nullable=False,
                      info={'label': 'Title'},
                      index=True)
    gamer_dynamics = db.Column(db.String(1024*16),
                               default='def define_variables(*args, **kwargs):\n'
                                              '\treturn {}\n'
                                              'def calculate_variables(old_variables, actions, gamer_id, *args, **kwargs):\n'
                                              '\treturn old_variables\n'
                                              'def is_next_round(current_round, *args, **kwargs):\n'
                                              '\treturn True\n'
                                              'def show_variables(old_variables, new_variables, actions, *args, **kwargs):\n'
                                              '\treturn ""',
                               info={'label': 'Gamer Dynamics', 'validators': utils.validate_code})
    game_trials = db.relationship('GameTrial',
                                  backref='game',
                                  lazy='dynamic',
                                  order_by="GameTrial.start_time.desc()")
    stages = db.relationship("Stage",
                          secondary="game_to_stage",
                          order_by="game_to_stage.c.order_number",
                          lazy='joined',
                          backref = db.backref('games', lazy='joined'))

def show_variables_wrapper(func):
    def inner(old_variables, new_variables, actions, *args, **kwargs):
        old_variables_cast = {k: utils.int_or_float_or_string(v) for k, v in old_variables.items()}
        new_variables_cast = {k: utils.int_or_float_or_string(v) for k, v in new_variables.items()}
        return func(old_variables_cast, new_variables_cast, actions, *args, **kwargs)
    return inner


def define_variables_wrapper(func):
    def inner(*args, **kwargs):
        return {k: str(v) for k, v in func(*args, **kwargs).items()}
    return inner


def calculate_variables_wrapper(func):
    def inner(old_variables, actions, gamer_id, *args, **kwargs):
        old_variables_cast = {k: utils.int_or_float_or_string(v) for k, v in old_variables.items()}
        new_variables = func(old_variables_cast, actions, gamer_id, *args, **kwargs)
        new_variables_cast = {k: str(v) for k, v in new_variables.items()}
        return new_variables_cast
    return inner


@event.listens_for(Game, 'load')
def receive_load(target, context):
    code = target.gamer_dynamics
    global_scope = utils.sandbox_scope.copy()
    local_scope = {}
    exec(code, global_scope, local_scope)
    target.define_variables = define_variables_wrapper(local_scope['define_variables'])
    target.calculate_variables = calculate_variables_wrapper(local_scope['calculate_variables'])
    target.is_next_round = local_scope['is_next_round']
    target.show_variables = show_variables_wrapper(local_scope['show_variables'])