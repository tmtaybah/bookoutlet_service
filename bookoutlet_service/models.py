from datetime import datetime

from flask_login import UserMixin
from flask_login import current_user
from itsdangerous import SignatureExpired, BadSignature
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

# local imports
from bookoutlet_service import db, login_manager, app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    img_file = db.Column(db.String(20), nullable=False, default="default2.png")
    password = db.Column(db.String(60), nullable=False)
    goodreads_id = db.Column(db.String(75), nullable=False)

    # OAuth tokens
    request_token = db.Column(db.String(120))
    request_secret = db.Column(db.String(120))

    access_token = db.Column(db.String(120))
    access_secret = db.Column(db.String(120))

    # below are methods for reseting a user's password
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config["SECRET_KEY"], expires_sec)
        return s.dumps({"user_id": self.id}).decode("utf-8")

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config["SECRET_KEY"])

        try:
            user_id = s.loads(token)["user_id"]
        except (SignatureExpired, BadSignature) as e:
            return None

        return User.query.get(user_id)

        # add get access token func?

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


# TODO: add timestamp
class BookoutletBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(320), nullable=False)
    series = db.Column(db.String(320), nullable=True)
    author = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    format = db.Column(db.String(20), nullable=False)  # edition
    scratch_n_dent = db.Column(db.Boolean, nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    link = db.Column(db.String(75), nullable=False)

    def __eq__(self, other):
        if other != None:
            # print('{} == {}? {}'.format(self.title, other.title, self.title == other.title))
            # print('{} == {}? {}'.format(self.author, other.author, self.author == other.author))
            # print('{} == {}? {}'.format(self.format, other.format, self.format == other.format))
            # print('{} == {}? {}'.format(self.price, other.price, self.price == other.price))

            return (
                self.title == other.title
                and self.author == other.author
                and self.format == other.format
                and self.price == other.price
            )

        else:
            return False

    def __repr__(self):
        return f"Bookoutlet Book: {self.title} by {self.author}"


class GoodreadsBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(320), nullable=False)
    title_series = db.Column(db.String(320), nullable=True)
    author = db.Column(db.String(120), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Goodreads Book: {self.title} by {self.author}"
