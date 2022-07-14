from flask_login import login_required, current_user
from flask import render_template, request, Blueprint, jsonify, redirect, url_for, flash
from blogapp import db
from blogapp.models import User, Friends, UserProfile
from blogapp.decorators import count_friend_request
from blogapp.helpers import friend_list

friends = Blueprint('friends', __name__)


@friends.route('/suggested_friends/', methods=['GET', 'POST'])
@login_required
@count_friend_request
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

    if not friend_request:
        flash('There is No Friends Request', 'info')

    return render_template('friend_request.html', title="friends-request", friend_requests=friend_request)


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

    is_blocked = False  # To fetch a block user we passed static is_blocked in friend_list function

    """called friend_list function from helpers.py to fetch all friends"""
    friends_list = friend_list(is_blocked)

    """THIS QUERY FETCH ALL FRIENDS FROM FRIEND TABLE WHICH IN LIST2"""
    all_friends_list = User.query.filter(User.id.in_(friends_list)).filter(User.id != current_user.id).all()
    if not all_friends_list:
        flash('There is no Friends, Please add some friends first..!', 'info')

    return render_template('friend_list.html', title="friends", friends=all_friends_list)


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
        if current_user.is_authenticated:
            return redirect(url_for('main.home'))
        else:
            return redirect(url_for('users.login'))


@friends.route('/block_list/', methods=['GET', 'POST'])
@login_required
def block_list():
    if request.method == 'POST':
        friend_id = request.form["block_friend_id"]

        unblock_friend_obj = Friends.query.filter(
            (Friends.sender_id == current_user.id) | (Friends.receiver_id == current_user.id)).filter(
            (Friends.sender_id == friend_id) | (Friends.receiver_id == friend_id)).filter(
            Friends.is_blocked == True).first()

        unblock_friend_obj.is_blocked = False
        db.session.commit()

    is_blocked = True  # To fetch a block user we passed static is_blocked in friend_list function

    """called friend_list function from helpers.py to fetch all friends"""
    friends_list = friend_list(is_blocked)

    """THIS QUERY FETCH ALL FRIENDS FROM FRIEND TABLE WHICH IN LIST2"""
    all_friends_list = User.query.filter(User.id.in_(friends_list)).filter(User.id != current_user.id).all()
    if not all_friends_list:
        flash('There is a no block user', 'info')

    return render_template('block_list.html', title="block-list", block_friends=all_friends_list)


@friends.route('/search/', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        search_obj = request.form["search"]

        """
        THIS QUERY RETURN LIST OF USER'S ID 
        WHICH FIRSTNAME AND LASTNAME HAVE 
        SEARCH VALUE WHICH USER PASSED
        """
        look_for = '%{0}%'.format(search_obj)
        user_obj = UserProfile.query \
            .with_entities(UserProfile.user_id) \
            .filter((UserProfile.firstname.ilike(look_for)) | (UserProfile.lastname.ilike(look_for))) \
            .filter(UserProfile.user_id != current_user.id).all()

        user_list = []
        for i in user_obj:
            user_list.append(i[0])

        """
        GET ALL USERS WHICH IN USER LIST
        """
        search_users = User.query.filter(User.id.in_(user_list)).all()

        if not search_users:
            flash('No users', 'info')

        list_of_friends = friend_list(is_blocked=False)  # list of friend from helpers.py

        '''GET ALL PENDING REQUEST FRIENDS LIST'''
        pending_friend_requests = friend_list(is_blocked=False, status='pending')

    else:
        if current_user.is_authenticated:
            return redirect(url_for('main.home'))
        else:
            return redirect(url_for('users.login'))

    return render_template('search.html', lis=list_of_friends, all_search_user=search_users,
                           pending_friend_requests=pending_friend_requests)
