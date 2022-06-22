from flask_login import current_user
from blogapp.models import Friends
from functools import wraps

def count_friend_request(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        friend_request = Friends.query.filter(current_user.id == Friends.receiver_id).count()
        return fn(friend_request,*args, **kwargs)

    return decorated_view