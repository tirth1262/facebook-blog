from blogapp import db
from flask import render_template, redirect, flash, url_for, Blueprint, request, abort
from blogapp.posts.forms import PostForm
from blogapp.models import Post, Likes
from flask_login import current_user, login_required
from blogapp.posts.utils import save_picture

posts = Blueprint('posts', __name__)


@posts.route('/post/<int:post_id>')
def post(post_id):
    post_obj = Post.query.get_or_404(post_id)
    return render_template('post.html',
                           title=post_obj.title, post=post_obj)


@posts.route('/post/like/<int:post_id>',methods=['GET','POST'])
def like_post(post_id):

    condition = True
    like_obj = Likes(user_id=current_user.id, post_id=post_id, like=True)
    db.session.add(like_obj)
    db.session.commit()
    return redirect(url_for('main.home', condition=condition))


@posts.route('/post/dislike/<int:post_id>',methods=['GET','POST'])
def dislike_post(post_id):
    condition = False
    lke = Likes.query.filter(current_user.id==Likes.user_id).filter(Likes.post_id==post_id).filter(Likes.like == False).first()
    delete_like = Likes.query.get(lke.id)
    delete_like.like = False
    db.session.commit()
    return redirect(url_for('main.home', condition=condition))

@posts.route('/post/<int:post_id>/update/', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
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

    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')


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
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        picture_file = save_picture(form.picture.data)
        post_obj = Post(title=form.title.data, content=form.content.data, is_public=form.is_public.data,
                        image_file=picture_file, author=current_user)
        db.session.add(post_obj)
        db.session.commit()
        flash(f'Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')

#
# @posts.route('/like/<int:post_id>/<action>')
# def like_action(post_id, action):
#     album = Post.query.filter_by(id=post_id).first_or_404()
#     likeunlike = action
#     if likeunlike == 'like':
#         current_user.like_album(album)
#         db.session.commit()
#         return "success", 200
#     if likeunlike == 'unlike':
#         current_user.unlike_album(album)
#         db.session.commit()
#         return "success", 200