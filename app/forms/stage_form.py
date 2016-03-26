from wtforms_alchemy import ModelForm
from app.models import Stage
from app import db

class StageForm(ModelForm):
    class Meta:
        model = Stage

    @classmethod
    def get_session(cls):
        return db.session

