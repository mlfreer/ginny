from flask import *
from app import app, db, manager_permission, login_required, socketio, current_user
from app.models import Game, GameTrial, Gamer, GamerAction, Room
from app.forms import GameForm, GameTrialForm
from datetime import datetime, timedelta
from flask_socketio import join_room, emit
from io import StringIO, BytesIO
from sqlalchemy.orm import class_mapper, ColumnProperty
import csv
import time



@socketio.on('connect', namespace='/gaming_manage')
def connect():
    if not current_user.is_anonymous and current_user.has_role('manager'):
        emit("connected", namespace='/gaming_manage', room=request.sid)
        return True
    return False

@socketio.on('tell_game_trial_id', namespace='/gaming_manage')
def tell(data):
    if not current_user.is_anonymous and current_user.has_role('manager'):
        join_room("GameTrial:{}".format(data['game_trial_id']))
        return True
    return False

@app.route('/game/<int:game_id>/trial/<int:id>')
@login_required
@manager_permission.require()
def game_trial(game_id, id):
    game_trial = GameTrial.query.filter(GameTrial.id == id).one()
    game = game_trial.game
    if game.id != game_id:
        abort(404)
    return render_template("game_trial/show.jade",
                            title = game.title,
                            form=GameTrialForm(obj=game_trial),
                            game=game,
                            game_trial=game_trial)

@app.route('/game/<int:game_id>/trial/new')
@login_required
@manager_permission.require()
def game_trial_new(game_id):
    game = Game.query.filter(Game.id == game_id).one()
    if game.id != game_id:
        abort(404)
    form = GameTrialForm()
    return render_template("game_trial/new.jade",
                            title = '{} | {}'.format(game.title, 'Create New Session'),
                            form=form,
                            game=game)

@app.route('/game/<int:game_id>/trial', methods=['POST'])
@login_required
@manager_permission.require()
def game_trial_create(game_id):
    game_trial = GameTrial()
    game = Game.query.filter(Game.id == game_id).one()
    if game.id != game_id:
        abort(404)
    form = GameTrialForm(request.form, obj=game_trial)
    if form.validate():
        form.populate_obj(game_trial)
        game_trial.start_time += timedelta(minutes=int(request.form['tz']))
        game_trial.game = game
        db.session.add(game_trial)
        db.session.commit()
        return redirect(url_for('game', id=game.id))
    return render_template("game_trial/new.jade",
                            title = '{} | {}'.format(game.title, 'Create New Session'),
                            form=form,
                            game=game)

@app.route('/game/<int:game_id>/trial/<int:id>', methods=['POST'])
@login_required
@manager_permission.require()
def game_trial_update(game_id, id):
    game_trial = GameTrial.query.filter(GameTrial.id == id).one()
    game = game_trial.game
    if game.id != game_id:
        abort(404)
    form = GameTrialForm(request.form, obj=game_trial)
    if form.validate():
        form.populate_obj(game_trial)
        game_trial.start_time += timedelta(minutes=int(request.form['tz']))
        flash("Successfully saved", 'info')
        db.session.commit()
    return render_template("game_trial/show.jade",
                                title = '{} | {}'.format(game.title, game_trial.start_time),
                                form=form,
                                game=game,
                                game_trial=game_trial)

@app.route('/game/<int:game_id>/trial/<int:id>/open', methods=['GET'])
@login_required
@manager_permission.require()
def game_trial_open_switch(game_id, id):
    game_trial = GameTrial.query.filter(GameTrial.id == id).one()
    game = game_trial.game
    if game.id != game_id:
        abort(404)
    if game_trial.started:
        abort(400)
    game_trial.opened = not game_trial.opened
    db.session.commit()
    return redirect(url_for('game_trial', game_id=game_id, id=id))

@app.route('/game/<int:game_id>/trial/<int:id>/start', methods=['GET'])
@login_required
@manager_permission.require()
def game_trial_start(game_id, id):
    game_trial = GameTrial.query.filter(GameTrial.id == id).one()
    game = game_trial.game
    if game.id != game_id:
        abort(404)
    try:
        game_trial.distribute_gamers()
        for room in game_trial.rooms:
            room.current_step = 0
        game_trial.started = True
        game_trial.opened = False
        db.session.commit()
        socketio.emit('started', namespace='/gaming', room="GameTrial:{}".format(game_trial.id))
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for('game_trial', game_id=game_id, id=id))

@app.route('/game/<int:game_id>/trial/<int:id>/finish', methods=['GET'])
@login_required
@manager_permission.require()
def game_trial_finish(game_id, id):
    game_trial = GameTrial.query.filter(GameTrial.id == id).one()
    game = game_trial.game
    if game.id != game_id:
        abort(404)
    try:
        game_trial.finished = True
        db.session.commit()
        socketio.emit('finished', namespace='/gaming', room='GameTrial:{}'.format(game_trial.id))
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for('game_trial', game_id=game_id, id=id))

@app.route('/game/<int:game_id>/trial/<int:id>/kick/<int:gamer_id>', methods=['GET'])
@login_required
@manager_permission.require()
def game_trial_kick(game_id, id, gamer_id):
    game_trial = GameTrial.query.filter(GameTrial.id == id).one()
    game = game_trial.game
    if game.id != game_id:
        abort(404)
    try:
        gamer = Gamer.query.filter(Gamer.id == gamer_id).one()
        if gamer.game_trial.started:
            abort(400)
        kicked_id = gamer.id
        db.session.delete(gamer)
        db.session.commit()
        socketio.emit('kicked', {'redirect-url': url_for('gaming_kicked')}, namespace='/gaming', room='Gamer:{}'.format(kicked_id))
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for('game_trial', game_id=game_id, id=id))

@app.route('/game/<int:game_id>/trial/<int:id>/gamer_actions.csv', methods=['GET'])
@login_required
@manager_permission.require()
def game_trial_download_gamer_actions(game_id, id):
    game_trial = GameTrial.query.filter(GameTrial.id == id).one()
    game = game_trial.game
    if game.id != game_id:
        abort(404)
    try:
        data = GamerAction.query.join(Room).filter(Room.game_trial_id == id).all()
        outstream = StringIO()
        outcsv = csv.writer(outstream)
        columns = ['room_id', 'round', 'stage', 'gamer_id', 'action', 'created_at']
        outcsv.writerow(columns)
        for row in data:
            r = []
            for c in columns:
                r.append(getattr(row,c))
            outcsv.writerow(r)
        outstream.seek(0)
        return send_file(outstream,
                     attachment_filename="{} - {} - Gamer Actions.csv".format(game.title, game_trial.start_time),
                     as_attachment=True)
    except ValueError as e:
        flash(str(e), "danger")

