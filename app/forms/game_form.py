from wtforms_alchemy import ModelForm
from wtforms.widgets import TextArea
from app.models import Game
from app import db, utils

class GameForm(ModelForm):
    class Meta:
        model = Game
        field_args = {'gamer_dynamics': {'widget': TextArea()}}

    @classmethod
    def get_session(cls):
        return db.session

