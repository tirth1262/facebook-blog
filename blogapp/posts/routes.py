from blogapp import db
from flask import render_template, redirect, flash, url_for, Blueprint, request, abort, jsonify
from blogapp.posts.forms import PostForm
from blogapp.models import Post, Likes
from flask_login import current_user, login_required
from blogapp.posts.utils import save_picture
from blogapp.decorators import count_friend_request


posts = Blueprint('posts', __name__)


@posts.route('/post/<int:post_id>')
def post(post_id):
    post_obj = Post.query.get_or_404(post_id)
    return render_template('post.html',
                           title=post_obj.title, post=post_obj)


@posts.route('/post/<int:post_id>/update/', methods=['GET', 'POST'])
@count_friend_request
@login_required
def update_post(post_id,friend_request=None):
    post_obj = Post.query.get_or_404(post_id)
    if post_obj.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post_obj.title = form.title.data
        post_obj.content = form.content.data
        db.session.commit()
        flash(f'Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post_id))
    elif request.method == 'GET':
        form.title.data = post_obj.title
        form.content.data = post_obj.content

    return render_template('create_post.html', title='Update Post', form=form, friend_request=friend_request, legend='Update Post')


@posts.route('/post/<int:post_id>/delete/', methods=['POST'])
@login_required
def delete_post(post_id):
    post_obj = Post.query.get_or_404(post_id)
    if post_obj.author != current_user:
        abort(403)
    db.session.delete(post_obj)
    db.session.commit()
    flash(f'Your post has been deleted!', 'success')

    return redirect(url_for('main.home'))


@posts.route('/post/new/', methods=['GET', 'POST'])
@count_friend_request
@login_required
def new_post(friend_request=None):
    form = PostForm()
    if form.validate_on_submit():
        path='images'
        size=500
        picture_file = save_picture(form.picture.data,size,path)
        post_obj = Post(title=form.title.data, content=form.content.data, is_public=form.is_public.data,
                        image_file=picture_file, author=current_user)
        db.session.add(post_obj)
        db.session.commit()
        flash(f'Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post', form=form, friend_request=friend_request, legend='New Post')


@posts.route('/like/', methods=['GET', 'POST'])
def like_action():
    if request.method == "POST":
        post_id = request.form['post_id']

        like_obj = Likes.query.filter_by(user_id=current_user.id, post_id=post_id, like=True).first()
        response = {}
        if like_obj:
            like = Likes.query.filter(Likes.user_id == current_user.id).filter(Likes.post_id == post_id).filter(
                Likes.like == True).first()
            delete_like = Likes.query.get(like.id)

            db.session.delete(delete_like)
            db.session.commit()
            response['like'] = False
        else:
            like = Likes(user_id=current_user.id, post_id=post_id, like=True)
            db.session.add(like)
            db.session.commit()
            response['like'] = True

        like_values = Likes.query.filter(post_id == Likes.post_id).count()
        response['like_value'] = like_values

        return jsonify(response)
    else:
        return redirect('main.home')