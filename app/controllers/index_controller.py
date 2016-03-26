from flask import *
from app import app, current_user, logout_user

@app.route('/')
def index():
    if current_user.is_anonymous:
        return render_template("index.jade",
                            title = 'Home')
    elif current_user.has_role('manager'):
        return redirect(url_for('manage'))
    elif current_user.has_role('admin'):
        return redirect(url_for('admin'))
    elif current_user.has_role('gamer'):
        return redirect(url_for('gaming'))