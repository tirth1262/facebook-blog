import pytest
from blogapp import create_app, db, bcrypt
from blogapp.models import User, Post, Comments
from datetime import datetime
import cloudinary


@pytest.fixture()
def app():
    app = create_app()
    cloudinary.config(cloud_name="dfmukiaes", api_key="644163589677663",
                      api_secret="D1uMam7aWjYQ1ki7ygzqDlKl6T0")
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "cloud_name": "dfmukiaes",
        "api_key": "644163589677663",
        "api_secret": "D1uMam7aWjYQ1ki7ygzqDlKl6T0"
    })

    # This creates an in-memory sqlite db
    # See https://martin-thoma.com/sql-connection-strings/
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

    with app.app_context():
        db.create_all()
        user1 = User(id=1, username="fooo", email="bar@gmail.com",
                     password=bcrypt.generate_password_hash('password@123').decode('utf-8'), is_active=True)
        user2 = User(id=2, username="tirth", email="tirth@gmail.com",
                     password=bcrypt.generate_password_hash('password@123').decode('utf-8'), is_active=True)

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        post1 = Post(id=1, title='Blog1', content='This is my first blo', image_file="1.jpg",
                     is_public=True, user_id=1)
        db.session.add(post1)
        db.session.commit()
        comment1 = Comments(id=1,user_id=1,post_id=1,message="nice",created_at=datetime.utcnow())
        db.session.add(comment1)
        db.session.commit()

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(scope='module')
def new_user():
    user = User(username='parth', email='parth.123@gmail.com', password='FlaskIsAwesome', is_active=True)
    return user


@pytest.fixture(scope='module')
def new_post():
    post = Post(title='Blog1', content='This is my first blog', image_file='default.jpg')
    return post


@pytest.fixture(scope='module')
def new_comment():
    comment = Comments(user_id=1, post_id=1, message='This is my first blog', created_at=datetime.utcnow)
    return comment


@pytest.fixture()
def login(client):
    """Login helper function"""
    response = client.post(
        "/login",
        data=dict(email="bar@gmail.com", password='password@123', remember='y'),
        follow_redirects=True
    )
    # print(f"RESPONSE LOGIN ******** {response.text}")
    return response


@pytest.fixture()
def register(client):
    """register helper function"""
    response = client.post(
        "/register",
        data=dict(username="smit", email="smit@gmail.com", password='Password@123', confirm_password='Password@123'),
        follow_redirects=True
    )
    # print(f"RESPONSE LOGIN ******** {response.text}")
    return response


