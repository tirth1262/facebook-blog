from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from blogapp.config import Config
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from flask_socketio import SocketIO

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()
oauth = OAuth()
socketio = SocketIO()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    oauth.init_app(app)
    socketio.init_app(app)

    with app.app_context():
        from blogapp.users.routes import users
        from blogapp.posts.routes import posts
        from blogapp.main.routes import main
        from blogapp.friends.routes import friends
        from blogapp.socialAuth.routes import socialAuth
        # from blogapp.chat.routes import chats

        app.register_blueprint(users)
        app.register_blueprint(posts)
        app.register_blueprint(main)
        app.register_blueprint(friends)
        app.register_blueprint(socialAuth)
        # app.register_blueprint(chats)

        return app
