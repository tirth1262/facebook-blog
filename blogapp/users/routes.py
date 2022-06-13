from blogapp import db, bcrypt, create_app
from flask import render_template, redirect, flash, url_for, Blueprint, request, current_app
from blogapp.users.forms import LoginForm, RegistrationForm, UpdateAccountForm, UpdatePassword
from blogapp.models import User, Post
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from blogapp.users.mail import send_email
from flask_login import login_user, current_user, logout_user, login_required

users = Blueprint('users', __name__)
v=current_app.config['MAIL_PASSWORD']
print("-----------------------------------------------------",v)
s = URLSafeTimedSerializer('5791628bb0b13ce0c676dfde280ba245')


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
        elif user.is_active == False:
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
        user = User(username=form.username.data,email=form.email.data,password=hs_pw)
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


@users.route('/account/', methods=['GET', 'POST'])
@login_required
def account():
    form=UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username=form.username.data
        current_user.email=form.email.data
        db.session.commit()
        flash(f'Your account has been updated!','success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    # image_file=url_for('static',filename='profile_pics/'+ current_user.image_file)
    # return render_template('account.html',title='Account',image_file=image_file,form=form)
    return render_template('account.html',title='Account',form=form)



@users.route('/user/<string:username>')
def user_posts(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.created_at.desc())
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
            current_user.password=hs_pw
            db.session.commit()
            flash('Your password has been Updated!','success')
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
