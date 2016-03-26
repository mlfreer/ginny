from flask import *
from app import app, db, manager_permission, login_required, socketio, current_user
from app.models import Game, GameTrial, Gamer, GamerAction, Room, Stage
from app.forms import GameForm, GameTrialForm, StageForm
from datetime import datetime, timedelta
from flask_socketio import join_room, emit
from io import StringIO, BytesIO
from sqlalchemy.orm import class_mapper, ColumnProperty
import csv
import time

@app.route('/stage/<int:id>')
@login_required
@manager_permission.require()
def stage(id):
    stage = Stage.query.filter(Stage.id == id).one()
    form = StageForm(obj=stage)
    return render_template("stage/show.jade",
                                title = 'Stages | {}'.format(stage.display_name),
                                form=form,
                                stage=stage)


@app.route('/stage/new')
@login_required
@manager_permission.require()
def stage_new():
    pass

@app.route('/stage', methods=['POST'])
@login_required
@manager_permission.require()
def stage_create():
    pass

@app.route('/stage/<int:id>', methods=['POST'])
@login_required
@manager_permission.require()
def stage_update(id):
    stage = Stage.query.filter(Stage.id == id).one()
    form = StageForm(request.form, obj=stage)
    if form.validate():
        form.populate_obj(stage)
        flash("Successfully saved", 'info')
        db.session.commit()
    return render_template("stage/show.jade",
                                title = 'Stages | {}'.format(stage.display_name),
                                form=form,
                                stage=stage)
