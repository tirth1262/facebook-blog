from flask import (render_template, Blueprint, flash,
                   request, current_app, url_for, redirect, session)
from flask_login import current_user, login_required
from blogapp.models import Post, User, UserProfile
from sqlalchemy import desc
from blogapp.decorators import count_friend_request
from blogapp.helpers import friend_list, post_likes
from blogapp import oauth, db
from flask_login import login_user

main = Blueprint('main', __name__)


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

@main.route('/login/google')
def google_login():
    google = oauth.create_client('google')
    redirect_uri = url_for('main.google_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


# Google authorize route
@main.route('/login/google/authorize')
def google_authorize():
    google = oauth.create_client('google')
    print("----------->",google)
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
                        password=current_app.config["GOOGLE_CLIENT_SECRET"],
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
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'openid email profile'},
)

# twitter=oauth.register(
#     name='twitter',
#     client_id=current_app.config["TWITTER_CLIENT_ID"],
#     client_secret=current_app.config["TWITTER_CLIENT_SECRET"],
#     api_base_url='https://api.twitter.com/1.1/',
#     request_token_url='https://api.twitter.com/oauth/request_token',
#     access_token_url='https://api.twitter.com/oauth/access_token',
#     authorize_url='https://api.twitter.com/oauth/authenticate',
#     # fetch_token=lambda: session.get('token'),  # DON'T DO IT IN PRODUCTION
# )


twitter=oauth.register(
    name='twitter',
    client_id=current_app.config['TWITTER_CLIENT_ID'],
    client_secret=current_app.config['TWITTER_CLIENT_SECRET'],
    request_token_url='https://api.twitter.com/oauth/request_token',
    request_token_params=None,
    access_token_url='https://api.twitter.com/oauth/access_token',
    access_token_params=None,
    authorize_url='https://api.twitter.com/oauth/authenticate',
    authorize_params=None,
    api_base_url='https://api.twitter.com/1.1/',
    client_kwargs={'scope': 'openid'},



)
@main.route('/login/twitter')
def twitter_login():
    twitter = oauth.create_client('twitter')
    redirect_uri = url_for('main.twitter_authorize', _external=True)
    return twitter.authorize_redirect(redirect_uri)


@main.route('/login/twitter/authorize')
def twitter_authorize():
    print("Hey")
    twitter = oauth.create_client('twitter')
    twitter.authorize_access_token()
    resp = twitter.get('account/verify_credentials.json')
    resp.raise_for_status()
    profile = resp.json()
    print("\n",profile,"\n")



# Github login route
@main.route('/login/github')
def github_login():
    github = oauth.create_client('github')
    redirect_uri = url_for('main.github_authorize', _external=True)
    return github.authorize_redirect(redirect_uri)


# Github authorize route
@main.route('/login/github/authorize')
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
                        password=current_app.config["GOOGLE_CLIENT_SECRET"],
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


# @main.route("/", methods=['GET', 'POST'])
@main.route('/home/', methods=['GET', 'POST'])
@login_required
@count_friend_request
def home(friend_request=None):
    page = request.args.get('page', 1, type=int)

    """Called friend_list function from helpers.py to fetch all friend list"""
    friends_list = friend_list(is_blocked=False)
    friends_list.append(current_user.id)  # This method add current user.id in list to show their posts

    """THIS QUERY FETCH ALL POSTS FROM POST TABLE WHICH AUTHOR IS CURRENT USER & CURRENT USER'S FRIENDS"""
    posts = Post.query.filter(Post.user_id.in_(friends_list)).order_by(desc(Post.created_at)).paginate(page=page,
                                                                                                       per_page=2)
    """THIS QUERY FETCH ALL FRIENDS USING FRIEND_LIST"""
    all_friends_list = User.query.filter((User.id != current_user.id)).filter(User.is_active == True).all()

    """THIS QUERY RETURN ALL TOTAL LIKES OF PARTICULAR POST FROM LIKES TABLE  """
    likes = post_likes()  # call post_likes function from helpers.py to fetch all-post-likes

    if not posts:
        flash('Create a new post and share your idea with us.', 'info')
    return render_template('home.html', posts=posts, friends=all_friends_list, friend_request=friend_request,
                           likes=likes)


@main.route('/about/')
def about():
    return render_template('about.html', title='About')

# CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
#
# google = oauth.register(
#     name='google',
#     server_metadata_url=CONF_URL,
#     client_kwargs={
#         'scope': 'openid email profile'
#     }
# )


# @main.route('/login/google/authorize')
# def google_authorize():
#     token = oauth.google.authorize_access_token()
#     user = token.get('userinfo')
#     print(f"\n{user.email}\n")
#     return "You are successfully signed in using google"
