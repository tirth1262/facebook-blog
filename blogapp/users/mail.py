from blogapp import mail
from flask import url_for, current_app
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message

s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])


def send_email(email):
    """
    THIS FUNCTION SEND EMAIL TO USER FOR EMAIL VALIDATION WHEN NEW USER REGISTRATION
    """
    token = s.dumps(email)
    msg = Message('confirm email', sender='noreply@demo.com', recipients=[email])
    link = url_for('users.confirm_mail', token=token, _external=True)
    msg.body = f'''To confirm your email, visit the following link:
{link}
If you did not make this request then simply ignore this Because this is a spam message.
'''
    mail.send(msg)

def reset_password(email):
    token = s.dumps(email)
    msg = Message('confirm email', sender='noreply@demo.com', recipients=[email])
    link = url_for('users.confirm_reset_password_mail', token=token, _external=True)
    msg.body = f'''To reset your password, visit the following link:
{link}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)
