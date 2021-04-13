from app import db, login
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from os import path


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    profile = db.relationship('Profile', backref='profile', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(id)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Post: {self.body}>'

    def get_date(self):
        time_diff = datetime.now() - self.timestamp
        if time_diff < timedelta(minutes=1):
            return 'just now'
        elif time_diff < timedelta(minutes=60):
            return f'{time_diff.seconds // 60} minutes ago'
        elif time_diff < timedelta(days=1):
            return f'today {self.timestamp.seconds // 60}:{self.timestamp.seconds // 60}'




class Profile(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    date_of_birth = db.Column(db.Date, index=True)
    gender = db.Column(db.String(1))
    info = db.Column(db.Text)
    last_seen = db.Column(db.DateTime, index=True, default=datetime.now())
    photo_id = db.Column(db.Integer, db.ForeignKey('media.id'))

    def __repr__(self):
        return f'<Profile of user {self.user_id}>'

    def update_info(self, gender, photo, info, date_of_birth):
        if gender:
            self.gender = gender
        #photo
        if info.split():
            self.info = info
        if date_of_birth:
           self.date_of_birth = date_of_birth


class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(120))

    def __repr__(self):
        return f'<Media id: {self.id}>'

    def make_path(self):
        self.path = path.join(f'/media/{date}/')


user_media = db.Table('user_media',
                      db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                      db.Column('media_id', db.Integer, db.ForeignKey('media.id'))
                      )
