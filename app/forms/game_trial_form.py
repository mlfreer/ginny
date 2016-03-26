from wtforms_alchemy import ModelForm
from app.models import GameTrial
from app import db

class GameTrialForm(ModelForm):
    class Meta:
        model = GameTrial
        field_args = {'start_time': {'format': '%m/%d/%Y %I:%M %p'}}
        only = ['start_time', 'size_of_room']

    @classmethod
    def get_session(cls):
        return db.session

