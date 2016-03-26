from flask import *
from app import app, db, bcrypt, login_required, login_user, logout_user, \
    current_user, identity_changed, Identity, AnonymousIdentity, socketio
from app.models import User, Gamer
from app.forms import LoginForm
@app.route('/login', methods=['GET', 'POST'])
def login():
    next = request.args.get('next')
    if current_user is not None and current_user.is_authenticated:
        return redirect(next or url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.email==form.email.data).first()
        if user is not None and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            identity_changed.send(current_app._get_current_object(),
                                  identity=Identity(user.get_id()))
            flash('Logged in successfully', 'info')
            return redirect(next or url_for('index'))
        else:
            flash('Email and/or password are incorrect', 'danger')
            return render_template('login.jade', form=form)
    return render_template('login.jade', form=form)

@app.route("/logout")
@login_required
def logout():
    if current_user.has_role('gamer'):
        if current_user.game_trial.started:
            if not current_user.room.is_finished():
                abort(400)
        else:
            socketio.emit("gamer_unregister", {"id": current_user.id}, namespace='/gaming_manage', room="GameTrial:{}".format(current_user.game_trial.id))
            db.session.delete(current_user)
            db.session.commit()
    logout_user()
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())
    return redirect(request.args.get('next') or url_for('index'))