from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from blogapp.config import Config
from flask_login import LoginManager

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from blogapp.users.routes import users
        from blogapp.posts.routes import posts
        from blogapp.main.routes import main

        app.register_blueprint(users)
        app.register_blueprint(posts)
        app.register_blueprint(main)

        return app
