from flask import *
from app import app, manager_permission
from app.models import Game
from app.models import Stage


@app.route('/manage')
@manager_permission.require()
def manage():
    return render_template("manage/index.jade",
                            title = 'Manage',
                            games=Game.query.order_by(Game.title).all(),
                            stages=Stage.query.order_by(Stage.id).all())