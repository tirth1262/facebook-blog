from flask_login import login_required, current_user
from flask import render_template, request, Blueprint, redirect, url_for, jsonify
from blogapp import db
from blogapp.models import User, Friends
from blogapp.decorators import count_friend_request


friends = Blueprint('friends', __name__)


@friends.route('/suggested_friends/', methods=['GET', 'POST'])
@count_friend_request
@login_required
def suggested_friends(friend_request=None):
    list1 = []
    query1 = Friends.query.with_entities(Friends.sender_id).filter(current_user.id == Friends.receiver_id).all()
    for a in query1:
        list1.append(a[0])

    query2 = User.query.filter(~User.id.in_(list1)) \
        .filter(current_user.id != User.id) \
        .filter(User.is_active == True).all()

    is_friend = Friends.query.with_entities(Friends.receiver_id)\
        .filter(current_user.id == Friends.sender_id)\
        .filter(Friends.status == 'pending').all()
    is_friend_list = []
    for a in is_friend:
        is_friend_list.append(a[0])
    return render_template('add_friend.html', friends=query2, friend_request=friend_request, lis=is_friend_list)


@friends.route('/friend_requests/', methods=['GET', 'POST'])
@login_required
def friend_requests():
    if request.method == 'POST':
        if 'friend_id' in request.form:
            friend_id = request.form["friend_id"]
            friend_obj = Friends.query.get(friend_id)
            friend_obj.status = 'accepted'
            db.session.commit()

        elif 'delete_id' in request.form:
            delete_friend_id = request.form["delete_id"]
            friend_obj = Friends.query.get(delete_friend_id)
            db.session.delete(friend_obj)
            db.session.commit()

    friend_request = Friends.query.filter(current_user.id == Friends.receiver_id).all()
    return render_template('friend_request.html', friend_requests=friend_request)


@friends.route('/all_friends/', methods=['GET', 'POST'])
@login_required
def all_friends():
    friends_list = Friends.query.filter(current_user.id == Friends.receiver_id).filter(Friends.status == 'accepted').all()
    return redirect(url_for('users.account'))

@friends.route('/add_friend_action/',methods=['GET','POST'])
@login_required
def add_friend_action():
    if request.method == 'POST':
        friend_id = request.form["friend_id"]
        friend_obj = Friends.query.filter_by(sender_id=current_user.id, receiver_id=friend_id, status="pending").first()
        response = {}
        if friend_obj:
            friend = Friends.query.get(friend_obj.id)
            db.session.delete(friend)
            db.session.commit()
            response['add_request'] = False
        else:
            friend = Friends(sender_id=current_user.id, receiver_id=friend_id)

            db.session.add(friend)
            db.session.commit()
            response['add_request'] = True

        return jsonify(response)
    else:
        return redirect()