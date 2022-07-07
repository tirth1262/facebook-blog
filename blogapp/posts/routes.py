from blogapp import db
from flask import render_template, redirect, flash, url_for, Blueprint, request, abort, jsonify, current_app
from blogapp.posts.forms import PostForm
from blogapp.models import Post, Likes, Comments
from flask_login import current_user, login_required
from blogapp.posts.utils import save_picture
from blogapp.decorators import count_friend_request
from sqlalchemy import desc, func
from blogapp.helpers import post_likes
import cloudinary
import cloudinary.uploader

posts = Blueprint('posts', __name__)
cloudinary.config(cloud_name=current_app.config["CLOUDINARY_NAME"], api_key=current_app.config["CLOUDINARY_API_ID"],
                  api_secret=current_app.config["CLOUDINARY_API_SECRET"])




@posts.route('/post/<int:post_id>')
@login_required
def post(post_id):
    page = request.args.get('page', 1, type=int)
    post_obj = Post.query.get_or_404(post_id)

    """THIS QUERY IS GET ALL LIKES OF POST USING POST ID"""
    likes = post_likes()  # call post_likes function from helpers.py to fetch all-post-likes

    post_comments = Comments.query.filter_by(post_id=post_id).paginate(page=page, per_page=2)

    return render_template('post.html',
                           title=post_obj.title,
                           post=post_obj, likes=likes, comments=post_comments)


@posts.route('/post/<int:post_id>/update/', methods=['GET', 'POST'])
@count_friend_request
@login_required
def update_post(post_id, friend_request=None):
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

    return render_template('create_post.html', title='Update Post',
                           form=form,
                           friend_request=friend_request,
                           legend='Update Post')


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
        file_to_upload = form.picture.data
        upload_result = cloudinary.uploader.upload(file_to_upload, folder='Post_images')
        post_obj = Post(title=form.title.data, content=form.content.data,
                        is_public=form.is_public.data,
                        image_file=upload_result['url'], author=current_user)
        db.session.add(post_obj)
        db.session.commit()
        flash(f'Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post',
                           form=form, friend_request=friend_request,
                           legend='New Post')


@posts.route('/like/', methods=['GET', 'POST'])
@login_required
def like_action():
    if request.method == "POST":
        post_id = request.form['post_id']

        """THIS QUERY CONFIRM THAT POST IS LIKED BY CURRENT_USER OR NOT"""
        like_obj = Likes.query.filter_by(user_id=current_user.id,
                                         post_id=post_id, like=True).first()
        response = {}
        if like_obj:
            delete_like = Likes.query.get(like_obj.id)
            db.session.delete(delete_like)
            db.session.commit()
            response['like'] = False
        else:
            like = Likes(user_id=current_user.id, post_id=post_id, like=True)
            db.session.add(like)
            db.session.commit()
            response['like'] = True

        """THIS QUERY FETCHED ALL LIKES OF POST USING POST_ID"""
        like_values = Likes.query.filter(post_id == Likes.post_id).count()
        response['like_value'] = like_values

        return jsonify(response)
    else:
        if current_user.is_authenticated:
            return redirect(url_for('main.home'))
        else:
            return redirect(url_for('users.login'))


@posts.route('/comment/', methods=['GET', 'POST'])
@login_required
def comment():
    if request.method == 'POST':
        """THIS TWO REQUEST METHOD GET A POST ID OF COMMENT AND MESSAGE OF COMMENT"""
        comment_post_id = request.form["comment_post_id"]
        input_tag = request.form["input_tag"]

        """THIS QUERY ADD COMMENT IN COMMENT TABLE"""
        comment_obj = Comments(user_id=current_user.id,
                               post_id=comment_post_id, message=input_tag)
        db.session.add(comment_obj)
        db.session.commit()

        return 'comment successfully.'
    else:
        if current_user.is_authenticated:
            flash('You not access this method', 'warning')
            return redirect(url_for('main.home'))
        else:
            flash('You not access this method', 'warning')
            return redirect(url_for('users.login'))


@posts.route('/delete_comment/', methods=['GET', 'POST'])
@login_required
def delete_comment():
    if request.method == 'POST':
        """THIS REQUEST METHOD GET A 'delete_comment_id'"""
        delete_comment_id = request.form["delete_comment_id"]

        """THIS QUERY DELETE COMMENT IN COMMENT TABLE"""
        comment_obj = Comments.query.get(delete_comment_id)
        db.session.delete(comment_obj)
        db.session.commit()

        return 'comment deleted successfully.'
    else:
        if current_user.is_authenticated:
            flash('You not access this method', 'warning')
            return redirect(url_for('main.home'))
        else:
            flash('You not access this method', 'warning')
            return redirect(url_for('users.login'))


@posts.route('/trending_post/', methods=['GET', 'POST'])
@login_required
@count_friend_request
def trending_post(friend_request=None):
    """THIS QUERY RETURN ALL TOTAL LIKES OF PARTICULAR POST FROM LIKES TABLE  """
    likes = post_likes()  # call post_likes function from helpers.py to fetch all-post-likes

    page = request.args.get('page', 1, type=int)
    list1 = Likes.query.with_entities(Likes.post_id, func.count(Likes.post_id)) \
        .group_by(Likes.post_id) \
        .order_by(desc(func.count(Likes.post_id))).all()
    list2 = []
    for i in list1:
        list2.append(i[0])

    trending_posts = Post.query.filter(Post.id.in_(list2)) \
        .filter(Post.is_public == True) \
        .paginate(page=page, per_page=2)

    return render_template('trending_post.html', title=trending_post, trending_posts=trending_posts,
                           friend_request=friend_request, likes=likes)
