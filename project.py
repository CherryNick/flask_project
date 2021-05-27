from app import app, db, socketio
from app.models import User, Post


# for flask shell
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}


if __name__ == '__main__':
    #app.run(debug=True)
    socketio.run(app, debug=True)
