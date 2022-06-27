from blogapp import db
from flask import render_template, redirect, flash, url_for, Blueprint, request, abort, jsonify
from blogapp.posts.forms import PostForm
from blogapp.models import Post, Likes, Comments, Friends, User
from flask_login import current_user, login_required
from blogapp.posts.utils import save_picture
from blogapp.decorators import count_friend_request
from sqlalchemy import desc, func

posts = Blueprint('posts', __name__)


@posts.route('/post/<int:post_id>')
@login_required
def post(post_id):
    page = request.args.get('page', 1, type=int)
    post_obj = Post.query.get_or_404(post_id)

    """THIS QUERY IS GET ALL LIKES OF POST USING POST ID"""
    likes = Likes.query.with_entities(Likes.post_id).filter(current_user.id == Likes.user_id).all()
    res = []
    for like in likes:
        res.append(like[0])

    post_comments = Comments.query.filter_by(post_id=post_id).paginate(page=page, per_page=2)

    return render_template('post.html',
                           title=post_obj.title, post=post_obj, likes=res, comments=post_comments)


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

    return render_template('create_post.html', title='Update Post', form=form, friend_request=friend_request,
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
        path = 'images'
        size = 500
        picture_file = save_picture(form.picture.data, size, path)
        post_obj = Post(title=form.title.data, content=form.content.data, is_public=form.is_public.data,
                        image_file=picture_file, author=current_user)
        db.session.add(post_obj)
        db.session.commit()
        flash(f'Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post', form=form, friend_request=friend_request,
                           legend='New Post')


@posts.route('/like/', methods=['GET', 'POST'])
def like_action():
    if request.method == "POST":
        post_id = request.form['post_id']

        """THIS QUERY CONFIRM THAT POST IS LIKED BY CURRENT_USER OR NOT"""
        like_obj = Likes.query.filter_by(user_id=current_user.id, post_id=post_id, like=True).first()
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
        return redirect('main.home')


@posts.route('/comment/', methods=['GET', 'POST'])
def comment():
    if request.method == 'POST':
        """THIS TWO REQUEST METHOD GET A POST ID OF COMMENT AND MESSAGE OF COMMENT"""
        comment_post_id = request.form["comment_post_id"]
        input_tag = request.form["input_tag"]

        """THIS QUERY ADD COMMENT IN COMMENT TABLE"""
        comment_obj = Comments(user_id=current_user.id, post_id=comment_post_id, message=input_tag)
        db.session.add(comment_obj)
        db.session.commit()

        return 'comment successfully.'


@posts.route('/delete_comment/', methods=['GET', 'POST'])
def delete_comment():
    if request.method == 'POST':
        """THIS REQUEST METHOD GET A 'delete_comment_id'"""
        delete_comment_id = request.form["delete_comment_id"]

        """THIS QUERY DELETE COMMENT IN COMMENT TABLE"""
        comment_obj = Comments.query.get(delete_comment_id)
        db.session.delete(comment_obj)
        db.session.commit()

        return 'comment deleted successfully.'


@posts.route('/trending_post/', methods=['GET', 'POST'])
@login_required
@count_friend_request
def trending_post(friend_request=None):
    page = request.args.get('page', 1, type=int)
    friends_list = []
    receiver_obj = Friends.query.with_entities(Friends.receiver_id).filter_by(sender_id=current_user.id,
                                                                              status='accepted', is_blocked=False).all()
    for i in receiver_obj:
        friends_list.append(i[0])

    """
    THIS QUERY IS GET ALL 'sender_id' FORM FRIENDS TABLE 
    WHICH 'receiver_id' IS 'current_user.id & STATUS IS 'accepted'
    """
    sender_obj = Friends.query.with_entities(Friends.sender_id).filter_by(receiver_id=current_user.id,
                                                                          status='accepted', is_blocked=False).all()
    for j in sender_obj:
        friends_list.append(j[0])

    set1 = set(friends_list)  # TO REMOVE DUPLICATES ID FROM FRIENDS_LIST WE USE THIS SET
    list2 = list(set1)
    list2.append(current_user.id)  # This method add current user.id in list to show their posts

    """THIS QUERY FETCH ALL POSTS FROM POST TABLE WHICH AUTHOR IS CURRENT USER & CURRENT USER'S FRIENDS"""

    friend_list = User.query.filter((User.id != current_user.id)).filter(User.is_active == True).all()

    """THIS QUERY RETURN ALL TOTAL LIKES OF PARTICULAR POST FROM LIKES TABLE  """
    likes = Likes.query.with_entities(Likes.post_id).filter(current_user.id == Likes.user_id).all()
    res = []
    for like in likes:
        res.append(like[0])
    page = request.args.get('page', 1, type=int)
    list1 = Likes.query.with_entities(Likes.post_id, func.count((Likes.post_id))) \
        .group_by(Likes.post_id) \
        .order_by(desc(func.count((Likes.post_id)))).all()
    list2 = []
    for i in list1:
        list2.append(i[0])

    trending_posts = Post.query.filter(Post.id.in_(list2)).filter(Post.is_public == True).paginate(page=page, per_page=2)
    return render_template('trending_post.html', title=trending_post, trending_posts=trending_posts, friend_request=friend_request, friends=friend_list, likes=res)
