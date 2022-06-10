from blogapp import mail
from flask import url_for, current_app
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_mail import Message

# s = URLSafeTimedSerializer(current_app.config.get(['SECRET_KEY']))
s = URLSafeTimedSerializer('5791628bb0b13ce0c676dfde280ba245')

def send_email(email):
    token = s.dumps(email)
    msg = Message('confirm email', sender='noreply@demo.com', recipients=[email])
    link = url_for('users.confirm_mail', token=token, _external=True)
    msg.body = f'Your link is {link}.'
    mail.send(msg)
