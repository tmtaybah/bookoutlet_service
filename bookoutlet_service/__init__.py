import os
import sys
import logging
from bookoutlet_service.tasks import make_celery
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

# logger setup
formatter = logging.Formatter(
    "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s"
)
handler = RotatingFileHandler("logs/app.log", maxBytes=1000000, backupCount=1)
handler.setLevel(logging.DEBUG)  # ignore anything less than INFO
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

# app configurations
app.config["SECRET_KEY"] = "fdd463775e10d6815b0e37f830f29ed0"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

# celery config
app.config["CELERY_BACKEND"] = "db+sqlite:///tasks.db"
app.config["CELERY_BROKER_URL"] = "amqp://localhost//"

# app initializations
celery = make_celery(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"  # set login view
login_manager.login_message_category = "info"  # customize login msg category


# mail interface configuration
app.config["MAIL_SERVER"] = "smtp.googlemail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("EMAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("EMAIL_PASSWORD")
mail = Mail(app)

from bookoutlet_service import routes
