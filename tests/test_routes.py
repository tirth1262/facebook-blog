from pathlib import Path


def test_trending_post(client, login):
    response = client.get("/trending_post", follow_redirects=True)
    assert '<title>Flask Blog - trending_post</title>' in str(response.data)


def test_trending_post_failure(client):
    response = client.get("/trending_post", follow_redirects=True)
    assert 'Please log in to access this page.' in response.text


def test_login(login):
    assert 'Login Successfully.' in str(login.data)
    assert login.request.path == "/home/"


def test_login_email(client):
    response = client.post(
        "/login",
        data=dict(email="ba@gmail.com", password='pasword@123', remember='y'),
        follow_redirects=True
    )
    assert 'Login Unsuccessful. Please check your email or password' in str(response.data)


def test_login_password(client):
    response = client.post(
        "/login",
        data=dict(email="bar@gmail.com", password='pasword@12', remember='y'),
        follow_redirects=True
    )
    assert 'Login Unsuccessful. Please check your email or password' in str(response.data)


def test_register(register):
    assert 'Your account has been created! You are now able to log in' in str(register.data)
    assert register.status == '200 OK'
    assert register.request.path == "/login/"


def test_register_email(client):
    response = client.post(
        "/register",
        data=dict(username="smit", email="bar@gmail.com", password='Password@123', confirm_password='Password@123'),
        follow_redirects=True
    )
    assert 'That email is taken. Please try a another email' in response.text


def test_register_password(client):
    response = client.post(
        "/register",
        data=dict(username="smit", email="smit.123@gmail.com", password='Password@123', confirm_password='assword@123'),
        follow_redirects=True
    )
    assert 'Field must be equal to password.' in response.text


def test_register_password1(client):
    response = client.post(
        "/register",
        data=dict(username="smit", email="smit.123@gmail.com", password='password@123',
                  confirm_password='password@123'),
        follow_redirects=True
    )
    assert 'Password must have an uppercase character' in response.text


def test_register_password2(client):
    response = client.post(
        "/register",
        data=dict(username="smit", email="smit.123@gmail.com", password='password.', confirm_password='password.'),
        follow_redirects=True
    )
    assert 'Password must contain a number' in response.text


def test_new_post(client, login):
    resources = Path(__file__).parent / "resources"
    print(resources)
    response = client.post(
        "/post/new/",
        data=dict(id=5, title='Blog1', content='This is my first blog', picture=(resources / "1.jpg").open("rb"),
                  is_public=True),
        follow_redirects=True
    )
    assert response.status == '200 OK'
    assert 'Your post has been created!' in str(response.data)


def test_suggested_friends(client, login):
    response = client.get("/suggested_friends", follow_redirects=True)
    assert response.status == '200 OK'


def test_suggested_friends_failure(client):
    response = client.get("/suggested_friends", follow_redirects=True)
    assert 'Please log in to access this page.' in response.text


def test_update_password(client, login):
    response = client.post(
        "/update_password",
        data=dict(old_password='password@123', new_password='Password@1234', confirm_password='Password@1234'),
        follow_redirects=True
    )
    assert 'Your password has been Updated!' in str(response.data)


def test_update_password_failure(client):
    response = client.post(
        "/update_password",
        data=dict(old_password='password@123', new_password='Password@1234', confirm_password='Password@1234'),
        follow_redirects=True
    )
    assert 'Please log in to access this page.' in response.text


def test_update_password_failure1(client, login):
    response = client.post(
        "/update_password",
        data=dict(old_password='password@12', new_password='Password@1234', confirm_password='Password@1234'),
        follow_redirects=True
    )
    assert "Password Incorrect" in response.text


def test_update_password_failure2(client, login):
    response = client.post(
        "/update_password",
        data=dict(old_password='password@123', new_password='Password@1234', confirm_password='Password@123'),
        follow_redirects=True
    )
    assert "Field must be equal to new_password." in response.text


# Test case for block list with login
def test_block_list(client, login):
    response = client.get(
        "/block_list",
        follow_redirects=True
    )
    assert response.status == '200 OK'
    assert '<title>Flask Blog - block-list</title>' in str(response.data)


# Test case for block list without login
def test_block_list_failure(client):
    response = client.get(
        "/block_list",
        follow_redirects=True
    )
    assert "Please log in to access this page." in response.text


def test_all_friends(client, login):
    response = client.get(
        "/all_friends",
        follow_redirects=True
    )
    assert response.status == '200 OK'
    assert '<title>Flask Blog - friends</title>' in str(response.data)


def test_all_friends_failure(client):
    response = client.get(
        "/all_friends",
        follow_redirects=True
    )
    assert "Please log in to access this page." in response.text


def test_friend_requests(client, login):
    response = client.get(
        "/friend_requests",
        follow_redirects=True
    )
    assert response.status == '200 OK'
    assert '<title>Flask Blog - friends-request</title>' in str(response.data)


def test_friend_requests_failure(client):
    response = client.get(
        "/friend_requests",
        follow_redirects=True
    )
    assert "Please log in to access this page." in response.text


def test_home(client, login):
    response = client.get(
        "/home",
        follow_redirects=True
    )
    assert response.status == '200 OK'
    assert '<title>Flask Blog - Home</title>' in str(response.data)


def test_home_failure(client):
    response = client.get(
        "/home",
        follow_redirects=True
    )
    assert 'Please log in to access this page.' in str(response.data)


def test_update_post(client, login):
    resources = Path(__file__).parent / "resources"
    print(resources)
    response = client.post(
        "/post/1/update/",
        data=dict(title='Blog1', content='This is my first blo', picture=(resources / "1.jpg").open("rb"),
                  is_public=True),
        follow_redirects=True
    )
    assert 'Your post has been updated!' in str(response.data)


def test_delete_post(client, login):
    response = client.post(
        "/post/1/delete/",
        follow_redirects=True
    )
    assert 'Your post has been deleted!' in str(response.data)


def test_delete_post_failure(client, login):
    response = client.post(
        "/post/5/delete/",
        follow_redirects=True
    )
    assert response.status == '404 NOT FOUND'


def test_comment_new(client, login):
    response = client.post(
        "/comment",
        data=dict(user_id=1, post_id=1, message="nice"),
        follow_redirects=False
    )

    assert response.status == '308 PERMANENT REDIRECT'
    assert response.headers['Location'] == 'http://localhost/comment/'


def test_delete_comment(client, login):
    response = client.post(
        "/delete_comment",
        data=dict(delete_comment_id=1, user_id=1, post_id=1, message="nice"),
        follow_redirects=False
    )
    assert response.status == '308 PERMANENT REDIRECT'
    assert response.headers['Location'] == 'http://localhost/delete_comment/'


def test_comment_failure(client):
    response = client.post(
        "/comment",
        data=dict(user_id=1, post_id=1, message="nice"),
        follow_redirects=False
    )
    assert response.status == '308 PERMANENT REDIRECT'
    assert response.headers['Location'] == 'http://localhost/comment/'