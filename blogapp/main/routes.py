from flask import render_template, Blueprint, flash, request
from flask_login import current_user, login_required
from blogapp.models import Post, User, Likes, Friends
from sqlalchemy import desc
from blogapp.decorators import count_friend_request

main = Blueprint('main', __name__)


@main.route("/", methods=['GET', 'POST'])
@main.route('/home/', methods=['GET', 'POST'])
@count_friend_request
@login_required
def home(friend_request=None):
    page = request.args.get('page', 1, type=int)
    """
    THIS QUERY IS GET ALL 'receiver_id' FORM FRIENDS TABLE 
    WHICH 'sender_id' IS 'current_user.id & STATUS IS 'accepted'
    """
    friends_list = []
    receiver_obj = Friends.query.with_entities(Friends.receiver_id).filter_by(sender_id=current_user.id,
                                                                              status='accepted').all()
    for i in receiver_obj:
        friends_list.append(i[0])

    """
    THIS QUERY IS GET ALL 'sender_id' FORM FRIENDS TABLE 
    WHICH 'receiver_id' IS 'current_user.id & STATUS IS 'accepted'
    """
    sender_obj = Friends.query.with_entities(Friends.sender_id).filter_by(receiver_id=current_user.id,
                                                                          status='accepted').all()
    for j in sender_obj:
        friends_list.append(j[0])

    set1 = set(friends_list)  # TO REMOVE DUPLICATES ID FROM FRIENDS_LIST WE USE THIS SET
    list2 = list(set1)
    list2.append(current_user.id)  # This method add current user.id in list to show their posts

    """THIS QUERY FETCH ALL POSTS FROM POST TABLE WHICH AUTHOR IS CURRENT USER & CURRENT USER'S FRIENDS"""
    posts = Post.query.filter(Post.user_id.in_(list2)).order_by(desc(Post.created_at)).paginate(page=page, per_page=2)

    friend_list = User.query.filter((User.id != current_user.id)).filter(User.is_active == True).all()

    """THIS QUERY RETURN ALL TOTAL LIKES OF PARTICULAR POST FROM LIKES TABLE  """
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
