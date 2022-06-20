from flask_login import login_required, current_user
from flask import render_template, request, Blueprint, redirect, url_for
from blogapp import db
from blogapp.models import User, Friends

friends = Blueprint('friends', __name__)


@friends.route('/suggested_friends/', methods=['GET', 'POST'])
@login_required
def suggested_friends():
    if request.method == 'POST':
        friend_id = request.form["friend_id"]
        friend = Friends(sender_id=current_user.id, receiver_id=friend_id)
        db.session.add(friend)
        db.session.commit()

    friend_list = User.query\
        .filter(User.is_active == True)\
        .filter(current_user.id != User.id)\
        .all()
    print(friend_list)
    return render_template('add_friend.html', friends=friend_list)


@friends.route('/friend_requests/', methods=['GET', 'POST'])
def friend_requests():
    if request.method == 'POST':
        if 'friend_id' in request.form:
            friend_id = request.form["friend_id"]
            friend_obj = Friends.query.get(friend_id)
            # friend_obj.status = 'accepted'
            # db.session.commit()

        elif 'delete_id' in request.form:
            delete_friend_id = request.form["delete_id"]
            friend_obj = Friends.query.get(delete_friend_id)
            # db.session.delete(friend_obj)
            # db.session.commit()

    friend_request = Friends.query.filter(current_user.id == Friends.receiver_id).all()
    return render_template('friend_request.html', friend_requests=friend_request)


@friends.route('/all_friends/', methods=['GET', 'POST'])
@login_required
def all_friends():
    friends_list = Friends.query.filter(current_user.id == Friends.receiver_id).filter(Friends.status == 'accepted').all()
    print('-------------------',friends_list)
    return redirect(url_for('users.account'))