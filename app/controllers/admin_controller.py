from flask import *
from app import app, admin_permission, login_required, cache


@app.route('/admin')
@login_required
@admin_permission.require()
def admin():
    return render_template("admin/index.jade",
                            title = 'Administration')

@app.route('/admin/clear_cache')
@login_required
@admin_permission.require()
def clear_cache():
    cache.clear()
    return redirect(url_for('admin'))