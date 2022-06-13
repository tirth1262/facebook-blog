from flask import render_template, request, Blueprint, flash
from flask_login import current_user
from blogapp.models import Post

main = Blueprint('main',__name__)


@main.route("/")
@main.route('/home/')
def home():
    # page = request.args.get('page',1,type=int)
    # posts=Post.query.order_by(Post.date_posted.desc()).paginate(per_page=5)
    # return render_template('home.html',posts=posts,page=page)
    posts = Post.query.filter_by(user_id=current_user.id).all()
    if not posts:
        flash('Create a new post and share your idea with us.', 'info')
    return render_template('home.html', posts=posts)


@main.route('/about/')
def about():
    return render_template('about.html',title='About')