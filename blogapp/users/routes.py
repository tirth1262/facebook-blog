from blogapp import db, bcrypt
from flask import render_template, redirect, flash, url_for, Blueprint, request, current_app
from blogapp.users.forms import (LoginForm, RegistrationForm, UpdateAccountForm,
                                 UpdatePassword, ResetPasswordForm, RequestResetForm)
from blogapp.models import User, Post, UserProfile
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from blogapp.users.mail import send_email, reset_password
from flask_login import login_user, current_user, logout_user, login_required
from blogapp.posts.utils import save_picture
from sqlalchemy import desc

users = Blueprint('users', __name__)
s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])


@users.route('/', methods=['GET', 'POST'])
@users.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not (user and bcrypt.check_password_hash(user.password, form.password.data)):
            flash('Login Unsuccessful. Please check your email or password', 'danger')
        elif not user.is_active:
            flash('Login Unsuccessful. Please first verify your email', 'danger')
        else:
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))

    return render_template('login.html', title='login', form=form)


@users.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hs_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hs_pw)
        email = form.email.data
        send_email(email)
        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(email=email).first()
        profile = UserProfile(firstname=None, lastname=None, profile_image="default.jpg", birthday=None,
                              user_id=user.id)
        db.session.add(profile)
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


@users.route('/account/', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.picture.data:
                size = 125
                path = 'profile_pics'
                picture_file = save_picture(form.picture.data, size, path)
                current_user.user_profile.profile_image = picture_file
            current_user.username = form.username.data
            current_user.user_profile.firstname = form.firstname.data
            current_user.user_profile.lastname = form.lastname.data
            current_user.user_profile.birthday = form.birthday.data
            db.session.commit()
            flash(f'Your account has been updated!', 'success')
            return redirect(url_for('users.account'))
        else:
            print("form not valid")
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.firstname.data = current_user.user_profile.firstname
        form.lastname.data = current_user.user_profile.lastname
        form.birthday.data = current_user.user_profile.birthday

    return render_template('account.html', title='Account', form=form, condition=True)


@users.route('/user/<string:username>')
@login_required
def user_posts(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(desc(Post.created_at))
    return render_template('user_posts.html', posts=posts, user=user)


@users.route('/update_password/', methods=['GET', 'POST'])
@login_required
def update_password():
    form = UpdatePassword()
    if form.validate_on_submit():
        if not bcrypt.check_password_hash(current_user.password, form.old_password.data):
            flash('Password Incorrect', 'danger')
        else:
            hs_pw = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            current_user.password = hs_pw
            db.session.commit()
            flash('Your password has been Updated!', 'success')
            return redirect(url_for('main.home'))

    return render_template('update_password.html', title='Update password', form=form)


@users.route('/confirm/<token>/', methods=['GET', 'POST'])
def confirm_mail(token):
    try:
        email = s.loads(token, max_age=3600)
        user = User.query.filter_by(email=email).first()
        user.is_active = True
        db.session.commit()
    except SignatureExpired:
        return 'token expired'

    return redirect(url_for('users.login'))


@users.route('/reset_password/<token>/', methods=['GET', 'POST'])
def confirm_reset_password_mail(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        reset_password(user.email)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)
