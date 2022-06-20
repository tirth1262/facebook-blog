from blogapp import db, bcrypt
from flask import render_template, redirect, flash, url_for, Blueprint, request, current_app
from blogapp.users.forms import LoginForm, RegistrationForm, UpdateAccountForm, UpdatePassword
from blogapp.models import User, Post, UserProfile, Friends
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from blogapp.users.mail import send_email
from flask_login import login_user, current_user, logout_user, login_required
from blogapp.posts.utils import save_profile_picture
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
        # image_file = url_for('static', filename='profile_pics/' + 'default.jpg')
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
                picture_file = save_profile_picture(form.picture.data)
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

    return render_template('account.html', title='Account', form=form, condition=True )


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


