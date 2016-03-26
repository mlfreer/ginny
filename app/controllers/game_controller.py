from flask import *
from app import app, db
from app.models import Game, GameTrial
from app.forms import GameForm
from app import manager_permission, login_required


@app.route('/game/<int:id>')
@login_required
@manager_permission.require()
def game(id):
    game = Game.query.filter(Game.id == id).one()
    form = GameForm(obj=game)
    return render_template("game/show.jade",
                            title = game.title,
                            form=form,
                            game=game)
@app.route('/game/new')
@login_required
@manager_permission.require()
def game_new():
    form = GameForm()
    return render_template("game/new.jade",
                            title = "New Game",
                            form=form)

@app.route('/game/new', methods=['POST'])
@login_required
@manager_permission.require()
def game_create():
    form = GameForm(request.form)
    if form.validate():
        game = Game()
        form.populate_obj(game)
        db.session.add(game)
        db.session.commit()
        return redirect(url_for('game', id=game.id))
    db.session.rollback()
    return render_template("game/new.jade",
                            title = "New Game",
                            form=form)

@app.route('/game/<int:id>', methods=['POST'])
@login_required
@manager_permission.require()
def game_update(id):
    game = Game.query.filter(Game.id == id).first()
    form = GameForm(request.form, obj=game)
    if form.validate():
        form.populate_obj(game)
        db.session.commit()
    else:
        db.session.rollback()
    return render_template("game/show.jade",
                            title = game.title,
                            form=form,
                            game=game)