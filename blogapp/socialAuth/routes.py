from flask import Blueprint, current_app, url_for, redirect
from blogapp import oauth, db
from flask_login import login_user
from blogapp.models import User, UserProfile

socialAuth = Blueprint('socialAuth', __name__)

google = oauth.register(
    name='google',
    client_id=current_app.config["GOOGLE_CLIENT_ID"],
    client_secret=current_app.config["GOOGLE_CLIENT_SECRET"],
    access_token_url='https://accounts.google.com/o/oauth2/token',
    AUTH0_DOMAIN="http://127.0.0.1:5000/home",
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs'
)


@socialAuth.route('/login/google')
def google_login():
    google = oauth.create_client('google')
    redirect_uri = url_for('socialAuth.google_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


# Google authorize route
@socialAuth.route('/login/google/authorize')
def google_authorize():
    google = oauth.create_client('google')
    google.authorize_access_token()
    resp = google.get('userinfo').json()
    user_email = resp['email']
    user = User.query.filter_by(email=user_email).first()
    if user:
        login_user(user)
        return redirect(url_for('main.home'))
    else:
        user_obj = User(username=resp['name'],
                        email=resp['email'],
                        password=current_app.config["PASSWORD"],
                        is_active=True)

        db.session.add(user_obj)
        db.session.commit()
        # user = User.query.filter_by(email=resp['email']).first()
        profile = UserProfile(firstname=None, lastname=None, profile_image=resp['picture'], birthday=None,
                              user_id=user_obj.id)
        db.session.add(profile)
        db.session.commit()
        login_user(user)
        return redirect(url_for('main.home'))


github = oauth.register(
    name='github',
    client_id=current_app.config["GITHUB_CLIENT_ID"],
    client_secret=current_app.config["GITHUB_CLIENT_SECRET"],
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com',
    client_kwargs={'scope': 'openid email profile'},
)


# Github login route
@socialAuth.route('/login/github')
def github_login():
    github = oauth.create_client('github')
    redirect_uri = url_for('socialAuth.github_authorize', _external=True)
    return github.authorize_redirect(redirect_uri)


# Github authorize route
@socialAuth.route('/login/github/authorize')
def github_authorize():
    github = oauth.create_client('github')
    github.authorize_access_token()
    resp = github.get('user').json()
    user_email = resp['email']
    user = User.query.filter_by(email=user_email).first()
    if user:
        login_user(user)
        return redirect(url_for('main.home'))
    else:
        user_obj = User(username=resp['name'],
                        email=resp['email'],
                        password=current_app.config["PASSWORD"],
                        is_active=True)

        db.session.add(user_obj)
        db.session.commit()
        # user = User.query.filter_by(email=resp['email']).first()
        profile = UserProfile(firstname=None, lastname=None, profile_image=resp['avatar_url'], birthday=None,
                              user_id=user_obj.id)
        db.session.add(profile)
        db.session.commit()
        login_user(user)
        return redirect(url_for('main.home'))


linkedin = oauth.register(
    name='linkedin',
    client_id=current_app.config["LINKED_CLIENT_ID"],
    client_secret=current_app.config["LINKED_CLIENT_SECRET"],
    AUTH0_DOMAIN="http://127.0.0.1:5000/home",
    access_token_method='POST',
    access_token_url='https://www.linkedin.com/uas/oauth2/accessToken',
    authorize_url='https://www.linkedin.com/uas/oauth2/authorization',
    access_token_params=None,
    authorize_params=None,
    api_base_url='https://api.linkedin.com/v2/',
    client_kwargs={'scope': 'r_emailaddress r_liteprofile'},

)


# Github login route
@socialAuth.route('/login/linkedin')
def linkedin_login():
    linkedin = oauth.create_client('linkedin')
    redirect_uri = url_for('socialAuth.linkedin_authorize', _external=True)
    return linkedin.authorize_redirect(redirect_uri)


# Github authorize route
@socialAuth.route('/login/linkedin/authorize')
def linkedin_authorize():
    linkedin = oauth.create_client('linkedin')
    linkedin.authorize_access_token()
    print(linkedin)

    email_address_json = linkedin.get('/v2/emailAddress?q=members&projection=(elements*(handle~))').json()
    email_address = email_address_json['elements'][0]['handle~']['emailAddress']
    resp = linkedin.get('me').json()
    user = User.query.filter_by(email=email_address).first()
    if user:
        login_user(user)
        return redirect(url_for('main.home'))
    else:
        firstname = (resp['firstName']['localized']['en_US'])
        lastname = (resp['lastName']['localized']['en_US'])
        user_obj = User(username=firstname,
                        email=email_address,
                        password=current_app.config["PASSWORD"],
                        is_active=True)

        db.session.add(user_obj)
        db.session.commit()
        # user = User.query.filter_by(email=resp['email']).first()
        profile = UserProfile(firstname=firstname, lastname=lastname, profile_image="default.jpg", birthday=None,
                              user_id=user_obj.id)
        db.session.add(profile)
        db.session.commit()
        login_user(user_obj)
        return redirect(url_for('main.home'))

    return 'done'


facebook = oauth.register(
    name='facebook',
    client_id=current_app.config["FACEBOOK_CLIENT_ID"],
    client_secret=current_app.config["FACEBOOK_CLIENT_SECRET"],
    access_token_url='https://graph.facebook.com/oauth/access_token',
    access_token_params=None,
    authorize_url="https://graph.facebook.com/oauth/authorize",
    authorize_params=None,
    api_base_url='https://api.facebook.com/',
    client_kwargs={'scope': 'openid email profile'},
)


# Github login route
@socialAuth.route('/login/facebook')
def facebook_login():
    facebook = oauth.create_client('facebook')
    redirect_uri = url_for('socialAuth.facebook_authorized', _external=True)
    return facebook.authorize_redirect(redirect_uri)


# Github authorize route
@socialAuth.route('/login/facebook/authorized')
def facebook_authorized():
    facebook = oauth.create_client('facebook')
    facebook.authorize_access_token()
    resp = facebook.get('user').json()
    print(resp)

    return resp


twitter = oauth.register(
    name='twitter',
    client_id=current_app.config['TWITTER_CLIENT_ID'],
    client_secret=current_app.config['TWITTER_CLIENT_SECRET'],
    api_base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',

)


@socialAuth.route('/login/twitter')
def twitter_login():
    redirect_uri = url_for('socialAuth.twitter_authorize', _external=True)
    return oauth.twitter.authorize_redirect(redirect_uri)


@socialAuth.route('/login/twitter/authorize')
def twitter_authorize():
    token = oauth.twitter.authorize_access_token()
    url = 'account/verify_credentials.json'
    resp = oauth.twitter.get(url, params={'skip_status': True})
    user = resp.json()
    print(user)
    return user
