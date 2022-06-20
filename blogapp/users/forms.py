from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from blogapp.models import User
from flask_wtf.file import FileField, FileAllowed


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me ')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=8, message="Password be at least 8 characters"),
                                         Regexp("^(?=.*[a-z])", message="Password must have a lowercase character"),
                                         Regexp("^(?=.*[A-Z])", message="Password must have an uppercase character"),
                                         Regexp("^(?=.*\\d)", message="Password must contain a number"),
                                         Regexp(
                                             "(?=.*[@$!%*#?&])", message="Password must contain a special character")])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please try a another email')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = EmailField('Email')
    firstname = StringField('First name', validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Last name', validators=[DataRequired(), Length(min=2, max=20)])
    birthday = DateField('Birth Date', validators=[DataRequired()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')


    def validate_username(self, username):
        if current_user.username != username.data:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please try a another username')


class UpdatePassword(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password',
                                 validators=[DataRequired(), Length(min=8, message="Password be at least 8 characters"),
                                             Regexp("^(?=.*[a-z])", message="Password must have a lowercase character"),
                                             Regexp("^(?=.*[A-Z])",
                                                    message="Password must have an uppercase character"),
                                             Regexp("^(?=.*\\d)", message="Password must contain a number"),
                                             Regexp(
                                                 "(?=.*[@$!%*#?&])",
                                                 message="Password must contain a special character")])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Update')
