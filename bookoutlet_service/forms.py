import re

from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

# local imports
from bookoutlet_service.models import User


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    goodreads_id = StringField("Goodreads Profile Link", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    # below are methods to check for username and email uniqueness
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            err_msg = "This username is taken. Please choose a different one"
            raise ValidationError(err_msg)

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            err_msg = "This email is taken. Please choose a different one"
            raise ValidationError(err_msg)

    # takes a users Goodreads profile link and extracts the user id from it
    def id_cleanup(self, goodreads_username):
        id = goodreads_username.split("/")[-1]
        id = re.sub("^[0-9]", "", id)
        print(f"cleaned up id -- {id}")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")


class UpdateAccountForm(FlaskForm):
    # update-able fields
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Update")

    # checks new username & email agaisnt database, returns error if exists
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                err_msg = " Username is taken. Please choose a different one"
                raise ValidationError(err_msg)

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                err_msg = "This email is taken. Please choose a different one"
                raise ValidationError(err_msg)


class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            err_msg = "There is no account with that email. \
            You must register first."
            raise ValidationError(err_msg)


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Reset Password")
