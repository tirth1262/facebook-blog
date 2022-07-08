from blogapp import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer
from flask import current_app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, index=True, primary_key=True)
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    user_profile = db.relationship('UserProfile', backref='profile', uselist=False)
    friend = db.relationship('Friends', backref='friend', foreign_keys="[Friends.receiver_id]",lazy=True, uselist=False)
    sender = db.relationship('Friends', backref='sender', foreign_keys="[Friends.sender_id]",lazy=True, uselist=False)

    @staticmethod
    def verify_reset_token(token):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            email = s.loads(token, max_age=3600)
        except:
            return None
        return User.query.filter_by(email=email).first()

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(255), nullable=False)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.relationship('Likes',cascade="all,delete", backref='likes', lazy='dynamic')
    comments = db.relationship('Comments',cascade="all,delete", backref='comments', lazy='dynamic')
    user_obj = db.relationship('User' , backref='user_obj')

    def __repr__(self):
        return f"Post('{self.title}')"


class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=True)
    lastname = db.Column(db.String(50), nullable=True)
    profile_image = db.Column(db.String(200), nullable=True,default='http://res.cloudinary.com/dfmukiaes/image/upload/v1657192158'
                                                      '/Profile_images/mpzcu7l2ss1auzbha9lj.jpg')
    birthday = db.Column(db.Date, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Friends(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    is_blocked = db.Column(db.Boolean, default=False)
    user = db.relationship('User', backref='user', foreign_keys="[Friends.sender_id]",lazy=True, uselist=False)


class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    like = db.Column(db.Boolean, default=False)


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    message = db.Column(db.Text, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    comment_user = db.relationship('User', backref='comment_user')

