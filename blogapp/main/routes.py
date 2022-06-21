from flask import render_template, Blueprint, flash, request
from flask_login import current_user
from blogapp.models import Post, User, Likes
from sqlalchemy import desc
from sqlalchemy.orm import load_only
from blogapp import db

main = Blueprint('main', __name__)


@main.route("/", methods=['GET', 'POST'])
@main.route('/home/', methods=['GET', 'POST'])
def home():
    posts = Post.query.filter_by(user_id=current_user.id).order_by(desc(Post.created_at))
    friend_list = User.query.filter((User.id != current_user.id)).filter(User.is_active == True).all()
    likes=Likes.query.with_entities(Likes.post_id).filter(current_user.id==Likes.user_id).all()

    res=[]
    for like in likes:
        res.append(like[0])



    if not posts:
        flash('Create a new post and share your idea with us.', 'info')
    return render_template('home.html', posts=posts, friends=friend_list,likes=res)


@main.route('/about/')
def about():
    return render_template('about.html', title='About')
