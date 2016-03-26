import random
import string
from app import *
from app.models.room import Room
from decimal import Decimal
from sqlalchemy.ext.mutable import MutableDict

class GameTrial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    string_id = db.Column(db.String(16), unique=True)
    game_id = db.Column(db.ForeignKey('game.id'), nullable=False)
    size_of_room = db.Column(db.Integer, nullable=True, info={'label': 'Size of room'})
    rooms = db.relationship('Room', backref='game_trial', lazy='dynamic', order_by="Room.id")
    gamers = db.relationship('Gamer', backref='game_trial', lazy='dynamic', order_by="Gamer.id")
    start_time = db.Column(db.DateTime, nullable=False, info={'label': 'Starting time'})
    opened = db.Column(db.Boolean, nullable=False, server_default="False", default=False, info={'label': 'Opened'})
    finished = db.Column(db.Boolean, nullable=False, server_default="False", default=False, info={'label': 'Finished'})
    started = db.Column(db.Boolean, nullable=False, server_default="False", default=False, info={'label': 'Started'})

    def __init__(self, **kwargs):
        super(GameTrial, self).__init__(**kwargs)
        self.string_id = \
            ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits)
                    for _ in range (int(get_option('session_id_length'))))

    def __str__(self):
        return "{};{}(UTC)".format(self.id, self.start_time)

    def distribute_gamers(self):
        gamers_count = self.gamers.count()
        for r in self.rooms:
            db.session.delete(r)
        if gamers_count % self.size_of_room != 0:
            raise ValueError("There is no enough players to fulfil last room")
        number_of_rooms = int(gamers_count / self.size_of_room)
        random_order_gamers = [g for g in self.gamers]
        random.shuffle(random_order_gamers)
        for i in range(number_of_rooms):
            room = Room(game_trial=self, size=self.size_of_room)
            for order, gamer in enumerate(random_order_gamers[i*self.size_of_room:(i+1)*self.size_of_room]):
                gamer.order_number = order
                gamer.variables = self.game.define_variables()
                room.gamers.append(gamer)