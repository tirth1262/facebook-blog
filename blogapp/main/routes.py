from flask import render_template, Blueprint, flash, request
from flask_login import current_user
from blogapp.models import Post, User
from sqlalchemy import desc
from blogapp import db

main = Blueprint('main', __name__)


@main.route("/", methods=['GET', 'POST'])
@main.route('/home/', methods=['GET', 'POST'])
def home():
    condition=request.args.get('condition')
    posts = Post.query.filter_by(user_id=current_user.id).order_by(desc(Post.created_at))
    friend_list = User.query.filter((User.id != current_user.id)).filter(User.is_active == True).all()
    if not posts:
        flash('Create a new post and share your idea with us.', 'info')
    return render_template('home.html', posts=posts, friends=friend_list,condition=condition)


@main.route('/about/')
def about():
    return render_template('about.html', title='About')
