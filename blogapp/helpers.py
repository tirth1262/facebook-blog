from flask_login import current_user
from blogapp.models import Friends, Likes
from flask import flash


def friend_list(is_blocked,status='accepted'):

    list1 = []
    receiver_obj = Friends.query.with_entities(Friends.receiver_id).filter_by(sender_id=current_user.id,
                                                                              status=status,
                                                                              is_blocked=is_blocked).all()
    for i in receiver_obj:
        list1.append(i[0])

    """
       THIS QUERY IS GET ALL 'sender_id' FORM FRIENDS TABLE 
       WHICH 'receiver_id' IS 'current_user.id & STATUS IS 'accepted'
    """
    sender_obj = Friends.query.with_entities(Friends.sender_id).filter_by(receiver_id=current_user.id,
                                                                          status='accepted',
                                                                          is_blocked=is_blocked).all()
    for j in sender_obj:
        list1.append(j[0])

    set1 = set(list1)  # TO REMOVE DUPLICATES ID FROM LIST1 WE USE THIS SET
    list2 = list(set1)

    return list2


def post_likes():
    """THIS QUERY RETURN ALL TOTAL LIKES OF PARTICULAR POST FROM LIKES TABLE  """
    likes = Likes.query.with_entities(Likes.post_id).filter(current_user.id == Likes.user_id).all()
    res = []
    for like in likes:
        res.append(like[0])

    return res