from blogapp import db, bcrypt
from flask import render_template, redirect, flash, url_for, Blueprint, request
from blogapp.users.forms import LoginForm, RegistrationForm
from blogapp.models import User
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from blogapp.users.mail import send_email
from flask_login import login_user, current_user, logout_user, login_required

users = Blueprint('users', __name__)
s = URLSafeTimedSerializer('5791628bb0b13ce0c676dfde280ba245')


@users.route('/home')
@login_required
def hello():
    return render_template('home.html')


@users.route('/about')
@login_required
def about():
    return render_template('about.html')

@users.route('/', methods=['GET', 'POST'])
@users.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users.hello'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not (user and bcrypt.check_password_hash(user.password, form.password.data)):
            flash('Login Unsuccessful. Please check your email or password', 'danger')
        elif user.is_active == False:
            flash('Login Unsuccessful. Please first verify your email.', 'danger')
        else:
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('users.hello'))

    return render_template('login.html', title='login', form=form)


@users.route('/register/', methods=['GET', 'POST'])
def register():
    # if current_user.is_authenticated:
    #     return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hs_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hs_pw)
        email = form.email.data
        send_email(email)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You are now able to log in', 'success')
        flash('First verify your email.', 'info')
        return redirect(url_for('users.login'))

    return render_template('register.html', title='register', form=form)


@users.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('users.login'))


@users.route('/confirm/<token>', methods=['GET', 'POST'])
def confirm_mail(token):
    try:
        email = s.loads(token, max_age=3600)
        user = User.query.filter_by(email=email).first()
        user.is_active = True
        db.session.commit()

    except SignatureExpired:
        return 'token expired'
    return redirect(url_for('users.login'))
