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
    """THIS QUERY FETCH ALL 'sender_id' FROM FRIENDS TABLE  WHICH 'receiver_id' IS 'current_user.id """
    query1 = Friends.query.with_entities(Friends.sender_id).filter(current_user.id == Friends.receiver_id).all()
    for a in query1:
        list1.append(a[0])

    """THIS QUERY FETCH ALL 'receiver_id' FROM FRIENDS TABLE  WHICH 'sender_id' IS 'current_user.id """
    query3 = Friends.query.with_entities(Friends.receiver_id).filter(current_user.id == Friends.sender_id).filter(
        Friends.status == 'accepted').all()
    for b in query3:
        list1.append(b[0])

    """THIS QUERY RETURN ALL USER WHICH NOT IN 'LIST1' AND ALSO NOT 'CURRENT_USER'"""
    query2 = User.query.filter(~User.id.in_(list1)) \
        .filter(current_user.id != User.id) \
        .filter(User.is_active == True).all()

    """THIS QUERY CONFIRM USER IS FRIEND OF ANOTHER USER OR NOT """
    is_friend = Friends.query.with_entities(Friends.receiver_id) \
        .filter(current_user.id == Friends.sender_id) \
        .filter(Friends.status == 'pending').all()

    """ALL VALUES FETCHED BY 'is_friend' QUERY PUT IN THIS LIST"""
    is_friend_list = []
    for a in is_friend:
        is_friend_list.append(a[0])

    return render_template('add_friend.html', friends=query2, friend_request=friend_request, lis=is_friend_list)


@friends.route('/friend_requests/', methods=['GET', 'POST'])
@login_required
def friend_requests():
    """THIS FUNCTION HANDLE FRIENDS REQUEST
    AND CHANGE STATUS 'ACCEPTED' OR DELETE ID AS PER 'request_action'
    """
    if request.method == 'POST':
        friend_id = request.form["friend_request_id"]
        request_action = request.form["text"]

        friend_obj = Friends.query.get(friend_id)

        if request_action == "accept":
            friend_obj.status = 'accepted'
            db.session.commit()
        else:
            db.session.delete(friend_obj)
            db.session.commit()

    """THIS QUERY FETCHED ALL FRIENDS REQUEST FOR CURRENT USER"""
    friend_request = Friends.query.filter(current_user.id == Friends.receiver_id).filter(
        Friends.status == 'pending').all()

    return render_template('friend_request.html', friend_requests=friend_request)


@friends.route('/all_friends/', methods=['GET', 'POST'])
@login_required
def all_friends():
    """THIS FUNCTION USE FOR SHOW ALL FRIENDS OF CURRENT USER"""
    if request.method == 'POST':
        remove_friend_id = request.form["remove_friend_id"]
        action = request.form["text"]

        """
           THIS QUERY FETCHED ALL FRIENDS FROM FRIEND TABLE 
           WHICH 'sender_id is current_user.id' OR 'receiver_id is current_user.id'
           WHICH 'receiver_id is remove_friend_id' OR 'sender_id is remove_friend_id'
        """
        delete_friend_obj = Friends.query \
            .filter((Friends.sender_id == current_user.id) | (Friends.receiver_id == current_user.id)) \
            .filter((Friends.sender_id == remove_friend_id) | (Friends.receiver_id == remove_friend_id)) \
            .filter(Friends.status == "accepted").first()

        if action == 'remove':
            db.session.delete(delete_friend_obj)
            db.session.commit()
        else:
            delete_friend_obj.is_blocked = True
            db.session.commit()

    """
        THIS QUERY IS GET ALL 'receiver_id' FORM FRIENDS TABLE 
        WHICH 'sender_id' IS 'current_user.id & STATUS IS 'accepted'
    """
    list1 = []
    receiver_obj = Friends.query.with_entities(Friends.receiver_id).filter_by(sender_id=current_user.id,
                                                                              status='accepted', is_blocked=False).all()
    for i in receiver_obj:
        list1.append(i[0])

    """
       THIS QUERY IS GET ALL 'sender_id' FORM FRIENDS TABLE 
       WHICH 'receiver_id' IS 'current_user.id & STATUS IS 'accepted'
    """
    sender_obj = Friends.query.with_entities(Friends.sender_id).filter_by(receiver_id=current_user.id,
                                                                          status='accepted', is_blocked=False).all()
    for j in sender_obj:
        list1.append(j[0])

    set1 = set(list1)  # TO REMOVE DUPLICATES ID FROM LIST1 WE USE THIS SET
    list2 = list(set1)

    """THIS QUERY FETCH ALL FRIENDS FROM FRIEND TABLE WHICH IN LIST2"""
    friends_list = User.query.filter(User.id.in_(list2)).filter(User.id != current_user.id).all()

    return render_template('friend_list.html', friends=friends_list)


@friends.route('/add_friend_action/', methods=['GET', 'POST'])
@login_required
def add_friend_action():
    """THIS FUNCTION HANDLE ALL 'ADD FRIEND REQUESTS' AND 'UNDO' FRIENDS REQUEST """
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
        return None
