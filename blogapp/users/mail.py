from blogapp import mail
from flask import url_for, current_app
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message

s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])


def send_email(email):
    token = s.dumps(email)
    msg = Message('confirm email', sender='noreply@demo.com', recipients=[email])
    link = url_for('users.confirm_mail', token=token, _external=True)
    msg.body = f'Your link is {link}.'
    mail.send(msg)
