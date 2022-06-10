from blogapp import app, db, bcrypt
from flask import render_template, redirect, flash, url_for
from blogapp.forms import LoginForm, RegistrationForm
from blogapp.models import User


@app.route('/home')
def hello():
    return "<h1>Hello World!</h1>"


@app.route('/')
@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if not (user and bcrypt.check_password_hash(user.password, form.password.data)):
            flash('Login Unsuccessful. Please check your email or password', 'danger')
        elif user.is_active == False:
            flash('Login Unsuccessful. Please first verify your email.', 'danger')
        else:
            return redirect(url_for('hello'))

    return render_template('login.html', title='login', form=form)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    # if current_user.is_authenticated:
    #     return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hs_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hs_pw)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', title='register', form=form)
