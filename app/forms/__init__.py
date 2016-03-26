from flask_wtf import Form
from flask_wtf.file import FileField
from wtforms import StringField, TextAreaField, \
    SelectField, DateField, PasswordField,\
    FloatField, SelectMultipleField, IntegerField, DateTimeField, BooleanField,\
    validators

from app.forms.game_form import GameForm
from app.forms.game_trial_form import GameTrialForm
from app.forms.login_form import LoginForm
from app.forms.stage_form import StageForm
