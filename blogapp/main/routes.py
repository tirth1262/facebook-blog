from flask import render_template, Blueprint, flash
from flask_login import current_user,login_required
from blogapp.models import Post, User, Likes
from sqlalchemy import desc
from blogapp.decorators import count_friend_request


main = Blueprint('main', __name__)


@main.route("/", methods=['GET', 'POST'])
@main.route('/home/', methods=['GET', 'POST'])
@count_friend_request
@login_required
def home(friend_request=None):
    posts = Post.query.filter_by(user_id=current_user.id).order_by(desc(Post.created_at))
    friend_list = User.query.filter((User.id != current_user.id)).filter(User.is_active == True).all()
    likes = Likes.query.with_entities(Likes.post_id).filter(current_user.id == Likes.user_id).all()

    res = []
    for like in likes:
        res.append(like[0])

    if not posts:
        flash('Create a new post and share your idea with us.', 'info')
    return render_template('home.html', posts=posts, friends=friend_list, friend_request=friend_request, likes=res)


@main.route('/about/')
def about():
    return render_template('about.html', title='About')
