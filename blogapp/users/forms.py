from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from blogapp.models import User
from flask_wtf.file import FileField, FileAllowed
from datetime import date


class LoginForm(FlaskForm):
    """
    THIS FORM FOR USER LOGIN SYSTEM
    """
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me ')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    """
    THIS FORM FOR REGISTRATION OF NEW USER
    """
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

    def validate_username(self, username):
        """
        THIS FUNCTION IS VERIFY username OF USER IF IT'S ALREADY EXITS THEN THROW AN ERROR
        """
        user = User.query.filter_by(email=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please try a another username')

    def validate_email(self, email):
        """
        THIS FUNCTION IS VERIFY EMAIL OF USER IF IT'S ALREADY EXITS THEN THROW AN ERROR
        """
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please try a another email')


class UpdateAccountForm(FlaskForm):
    """
    THIS FORM FROM UPDATE USER DETAIL IN ACCOUNT FIELD.
    """
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = EmailField('Email')
    firstname = StringField('First name')
    lastname = StringField('Last name')
    birthday = DateField('Birth Date')
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        """
        THIS FUNCTION IS VERIFY USERNAME OF USER IF IT'S ALREADY EXITS THEN THROW AN ERROR
        """
        if current_user.username != username.data:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please try a another username')

    def validate_birthday(self, birthday):
        today = date.today()
        if birthday.data > today:
            raise ValidationError('Birthday is invalid, Please select valid Date')


class UpdatePassword(FlaskForm):
    """
    THIS IS UPDATE PASSWORD FORM FOR UPDATE PASSWORD
    """
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


class RequestResetForm(FlaskForm):
    """THIS FORM TAKE EMAIL AND FIRST VERIFY IT AND SEND MAIL AFTER SUBMIT"""
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    """THIS IS RESET PASSWORD FORM WITH TWO FIELDS PASSWORD AND CONFIRM PASSWORD"""
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=8, message="Password be at least 8 characters"),
                                         Regexp("^(?=.*[a-z])", message="Password must have a lowercase character"),
                                         Regexp("^(?=.*[A-Z])",
                                                message="Password must have an uppercase character"),
                                         Regexp("^(?=.*\\d)", message="Password must contain a number"),
                                         Regexp(
                                             "(?=.*[@$!%*#?&])",
                                             message="Password must contain a special character")])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
