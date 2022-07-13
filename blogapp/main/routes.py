from flask import (render_template, Blueprint, flash,jsonify,
                   request, current_app, url_for, redirect, session)
from flask_login import current_user, login_required
from blogapp.models import Post, User, UserProfile
from sqlalchemy import desc
from blogapp.decorators import count_friend_request
from blogapp.helpers import friend_list, post_likes


main = Blueprint('main', __name__)


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
                           likes=likes,title="Home")


@main.route('/about/')
def about():
    return render_template('about.html', title='About')


