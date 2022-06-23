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
    query3= Friends.query.with_entities(Friends.receiver_id).filter(current_user.id == Friends.sender_id).filter(Friends.status=='accepted').all()
    for b in query3:
        list1.append(b[0])
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
        friend_id = request.form["friend_request_id"]
        print(friend_id)
        request_action = request.form["text"]

        friend_obj = Friends.query.get(friend_id)

        if request_action == "accept":
            friend_obj.status = 'accepted'
            db.session.commit()
        else:
            db.session.delete(friend_obj)
            db.session.commit()

    friend_request = Friends.query.filter(current_user.id == Friends.receiver_id).filter(Friends.status=='pending').all()
    return render_template('friend_request.html', friend_requests=friend_request)


@friends.route('/all_friends/', methods=['GET', 'POST'])
@login_required
def all_friends():
    if request.method == 'POST':
        remove_friend_id = request.form["remove_friend_id"]
        action=request.form["text"]

        delete_friend_obj = Friends.query \
            .filter((Friends.sender_id == current_user.id) | (Friends.receiver_id == current_user.id)) \
            .filter((Friends.sender_id == remove_friend_id) | (Friends.receiver_id == remove_friend_id)) \
            .filter(Friends.status == "accepted").first()

        if action == 'remove':
            db.session.delete(delete_friend_obj)
            db.session.commit()
        else:
            delete_friend_obj.is_blocked=True
            db.session.commit()

    list1 = []
    receiver_obj = Friends.query.with_entities(Friends.receiver_id).filter_by(sender_id=current_user.id,
                                                                              status='accepted',is_blocked=False).all()
    for i in receiver_obj:
        list1.append(i[0])
    sender_obj = Friends.query.with_entities(Friends.sender_id).filter_by(receiver_id=current_user.id,
                                                                          status='accepted',is_blocked=False).all()
    for j in sender_obj:
        list1.append(j[0])
    set1 = set(list1)

    list2 = list(set1)
    friends_list= User.query.filter(User.id.in_(list2)).filter(User.id!=current_user.id).all()
    return render_template('friend_list.html',friends=friends_list)

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