from blogapp import db

class User(db.Model):
    id = db.Column(db.Integer, index=True, primary_key=True)
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=False)


    def __repr__(self):
        return '<User {}>'.format(self.username)