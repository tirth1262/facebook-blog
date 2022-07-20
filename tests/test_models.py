from datetime import datetime


def test_new_user(new_user):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, hashed_password, and role fields are defined correctly
    """

    assert new_user.username == 'parth'
    assert new_user.email == 'parth.123@gmail.com'
    assert new_user.password == 'FlaskIsAwesome'
    assert new_user.is_active == True


def test_new_post(new_post):
    """
    GIVEN a Post model
    WHEN a new Post is created
    THEN check the title, content, and image fields are defined correctly
    """
    assert new_post.title == 'Blog1'
    assert new_post.content == 'This is my first blog'
    assert new_post.image_file == 'default.jpg'


def test_new_comment(new_comment):
    """
    GIVEN a Comment model
    WHEN a new Comment is created
    THEN check the user_id, post_id, and message fields are defined correctly
    """
    assert new_comment.user_id == 1
    assert new_comment.post_id == 1
    assert new_comment.message == 'This is my first blog'
    assert new_comment.created_at == datetime.utcnow



