from app import db, login
from sqlalchemy.dialects.postgresql import ENUM
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from os import path, mkdir
import pathlib


class FriendRequest(db.Model):
    initiator_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    target_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    status = db.Column(ENUM('requested', 'approved', 'rejected', 'unfriended', name="friend_request_status"))
    requested_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    def approve_request(self):
        self.status = 'approved'

    def reject_request(self):
        self.status = 'rejected'

    def unfriend(self):
        self.status = 'unfriended'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    profile = db.relationship('Profile', backref='profile', uselist=False)
    requested_friend = db.relationship('FriendRequest', foreign_keys='FriendRequest.initiator_id',
                                       backref='requested_user', lazy='dynamic')
    received_friend = db.relationship('FriendRequest', foreign_keys='FriendRequest.target_id',
                                      backref='received_user', lazy='dynamic')
    messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='author')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def friend_list(self):
        return db.session.query(User).filter(User.id == FriendRequest.target_id,
                                             FriendRequest.initiator_id == self.id,
                                             FriendRequest.status == 'approved'
                                             ).union(
            db.session.query(User).filter(User.id == FriendRequest.initiator_id,
                                          FriendRequest.target_id == self.id,
                                          FriendRequest.status == 'approved')).all()

    def friends_posts(self):
        """Костыли какие то"""
        friends_id = [friend.id for friend in self.friend_list]
        friends = Post.query.filter(Post.user_id.in_(friends_id),
                                    Post.is_deleted == False)
        own = Post.query.filter_by(user_id=self.id, is_deleted=False)
        return friends.union(own).order_by(Post.timestamp.desc())

    def make_friend_request(self, target_user):
        friend_request = FriendRequest(initiator_id=self.id,
                                       target_id=target_user.id,
                                       status='requested')
        db.session.add(friend_request)
        db.session.commit()
        return friend_request

    def friend_status(self, user):
        friend_request = FriendRequest.query.filter_by(initiator_id=user.id,
                                                       target_id=self.id).first() or \
                         FriendRequest.query.filter_by(initiator_id=self.id,
                                                       target_id=user.id).first()
        if not friend_request:
            return None
        elif friend_request.status == 'requested' and friend_request.target_id == self.id:
            return 'requested_to'
        elif friend_request.status == 'requested' and friend_request.target_id == user.id:
            return 'requested_from'
        else:
            return friend_request.status

    def get_users_with_messages(self):
        """need to make order by last message"""
        return db.session.query(User).join(Message, User.id == Message.sender_id).filter(
            Message.receiver_id == self.id).union(
            db.session.query(User).join(Message, User.id == Message.receiver_id).filter(
                Message.sender_id == self.id))  # .order_by(Message.created_at.desc())

    def get_chat_with_user(self, user):
        return db.session.query(Message).filter_by(receiver_id=self.id, sender_id=user.id).union(
            db.session.query(Message).filter_by(receiver_id=user.id, sender_id=self.id).order_by(
                Message.created_at.desc()))


@login.user_loader
def load_user(id):
    return User.query.get(id)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    photo_id = db.Column(db.Integer, db.ForeignKey('media.id'))
    is_deleted = db.Column(db.Boolean, default=False)
    media = db.relationship('Media', back_populates='post')

    def __repr__(self):
        return f'<Post: {self.body}>'

    def get_date(self):
        month_to_str = {1: 'jan',
                        2: 'feb',
                        3: 'mar',
                        4: 'apr',
                        5: 'may',
                        6: 'jun',
                        7: 'jul',
                        8: 'aug',
                        9: 'sep',
                        10: 'oct',
                        11: 'nov',
                        12: 'dec'}

        time_diff = datetime.now() - self.timestamp
        if time_diff < timedelta(minutes=1):
            return 'just now'
        elif time_diff < timedelta(minutes=60):
            return f'{time_diff.seconds // 60} minutes ago'
        elif datetime.now().day - self.timestamp.day < 1:
            return f'today {self.timestamp.hour:0>2d}:{self.timestamp.minute:0>2d}'
        elif datetime.now().day - self.timestamp.day == 1:
            return f'yesterday {self.timestamp.hour:0>2d}:{self.timestamp.minute:0>2d}'
        elif datetime.now().year - self.timestamp.year < 1:
            return f'{self.timestamp.day} {month_to_str[self.timestamp.month]} ' \
                   f'{self.timestamp.hour:0>2d}:{self.timestamp.minute:0>2d}'
        else:
            return f'{self.timestamp.day} {month_to_str[self.timestamp.month]} {self.timestamp.year} ' \
                   f'{self.timestamp.hour:0>2d}:{self.timestamp.minute:0>2d}'

    def delete(self):
        self.is_deleted = True


class Profile(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    date_of_birth = db.Column(db.Date, index=True)
    gender = db.Column(db.String(1))
    info = db.Column(db.Text)
    last_seen = db.Column(db.DateTime, index=True, default=datetime.now())
    photo_id = db.Column(db.Integer, db.ForeignKey('media.id'))
    media = db.relationship('Media', back_populates='profile')

    def __repr__(self):
        return f'<Profile of user {self.user_id}>'

    def update_info(self, gender, photo, info, date_of_birth):
        if gender:
            self.gender = gender
        if photo:
            self.photo_id = photo
        if info.split():
            self.info = info
        if date_of_birth:
            self.date_of_birth = date_of_birth


class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(120))
    profile = db.relationship('Profile', back_populates='media')
    post = db.relationship('Post', back_populates='media')

    def __repr__(self):
        return f'<Media id: {self.id}>'

    def make_path(self, name):
        today_path = path.join(f'{pathlib.Path(__file__).parent.absolute()}', 'static', 'media', f'{date.today()}')
        if not path.isdir(today_path):
            mkdir(today_path)
        self.path = path.join('/', 'static', 'media', f'{date.today()}', f'{name}')

    def get_path(self):
        return self.path


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now())
