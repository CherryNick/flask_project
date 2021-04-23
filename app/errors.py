from app import app, db
from flask import render_template


@app.errorhandler(404)
def error404(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def error500(error):
    db.session.rollback()
    return render_template('500.html'), 500
