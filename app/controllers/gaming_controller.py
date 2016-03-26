from flask import *
from app import app, db, gamer_permission, identity_changed, Identity, current_user, socketio
from app.models import Game, GameTrial, Gamer, GamerAction, Room
from flask_login import login_user, logout_user
from flask_socketio import join_room, emit

from threading import Lock

gaming_lock = Lock()
id_to_sid = {}

@socketio.on('connect', namespace='/gaming')
def connect():
    if not current_user.is_anonymous and current_user.has_role('gamer'):
        join_room("Gamer:{}".format(current_user.id))
        join_room("GameTrial:{}".format(current_user.game_trial.id))
        if current_user.room is not None:
            join_room("Room:{}".format(current_user.room.id))
            emit("connected", {"room_size": current_user.room.size, 'moved': len(current_user.room.get_moved_gamers())}, namespace='/gaming', room="Gamer:{}".format(current_user.id))
        emit("gamer_connect", namespace='/gaming_manage', room="GameTrial:{}".format(current_user.game_trial.id))
        return True
    return False

@socketio.on('disconnect', namespace='/gaming')
def disconnect():
    if not current_user.is_anonymous and current_user.has_role('gamer'):
        emit("gamer_disconnect", namespace='/gaming_manage', room="GameTrial:{}".format(current_user.game_trial.id))

@app.route('/gaming', methods=['GET', 'POST'])
def gaming():
    if current_user.is_anonymous:
        return render_template("gaming/index.jade",
                                title = 'Home')
    elif current_user.has_role('gamer'):
        if current_user.game_trial.finished:
            return render_template("gaming/finish.jade")
        room = current_user.room
        if room is not None and current_user.game_trial.started:
            with gaming_lock:
                round = room.get_current_round()
                stage = room.get_current_stage()
                active_gamers = room.get_active_gamers()
                if len(active_gamers) == 0:

                    if room.is_last_stage():
                        room.calculate_variables()
                        for gamer in room.gamers:
                            gamer.show_results = True
                        if not room.game_trial.game.is_next_round(round + 1):
                            room.finished = True
                    room.current_step += 1
                    db.session.commit()
                    socketio.emit('new_round',
                                  namespace='/gaming_manage',
                                  room="GameTrial:{}".format(room.id))
                    round = room.get_current_round()
                    stage = room.get_current_stage()
                    active_gamers = room.get_active_gamers()

                if current_user.shown_results:
                    for gamer in room.gamers:
                        if not gamer.shown_results:
                            return render_template('gaming/await.jade')
                    for gamer in room.gamers:
                        gamer.show_results = False
                        gamer.shown_results = False
                        if gamer.id != current_user.id:
                            socketio.emit('all_shown',
                                          namespace='/gaming',
                                          room="Gamer:{}".format(gamer.id))
                    db.session.commit()
                    return redirect(url_for("gaming"))
                if current_user.show_results:
                    return render_template('gaming/result.jade',
                                           variables=current_user.get_show_variables())

                if current_user not in active_gamers:
                    return render_template('gaming/await.jade')

                if not room.is_finished():
                    if request.method == 'GET':
                        return render_template("gaming/game.jade",
                                               room=room,
                                               round=round,
                                               stage=stage,
                                               active=current_user in active_gamers)
                    elif request.method == "POST":
                        if current_user in active_gamers:
                            action = request.form['action-input']
                            gamer_action = GamerAction(room=room,
                                                       round=round,
                                                       stage=stage,
                                                       gamer=current_user,
                                                       action=action)
                            db.session.add(gamer_action)
                            db.session.commit()
                            for gamer in room.gamers:
                                if gamer.id != current_user.id:
                                    socketio.emit('moved',
                                              namespace='/gaming',
                                              room="Gamer:{}".format(gamer.id))
                        else:
                            flash("Action is forbidden")
                        return redirect(url_for('gaming'))
                else:
                    return render_template('gaming/finish.jade')
        else:
            return render_template("gaming/distribution_waiting.jade")
    elif current_user.has_role('manager') or current_user.has_role('admin'):
        flash("Action is forbidden")
        return redirect(url_for('index'))

@app.route('/gaming/join', methods=['POST'])
def gaming_join():
    if current_user.is_authenticated:
        flash("Action is forbidden")
        return redirect(url_for('index'))
    unique_id = request.form['unique-id']
    game_trial = GameTrial.query.filter(GameTrial.string_id == unique_id).one_or_none()
    if game_trial is None:
        flash("No game can be found by this Unique ID", "danger")
        return redirect(url_for("gaming"))
    elif not game_trial.opened:
        flash("Registration is closed", "danger")
        return redirect(url_for("gaming"))

    gamer = Gamer(game_trial=game_trial)
    db.session.add(gamer)
    db.session.commit()
    login_user(gamer)
    socketio.emit("gamer_register", {'id': gamer.id}, namespace='/gaming_manage', room="GameTrial:{}".format(game_trial.id))
    identity_changed.send(current_app._get_current_object(),
                                  identity=Identity(gamer.get_id()))
    return redirect(url_for('gaming'))

@app.route('/gaming/shown')
def gaming_shown():
    current_user.shown_results = True
    db.session.commit()
    return redirect(url_for('gaming'))

@app.route('/gaming/kicked')
def gaming_kicked():
    return render_template('gaming/kicked.jade')