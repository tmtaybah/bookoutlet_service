import time

from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

# local imports
from bookoutlet_service import app, db, bcrypt, mail, handler
from bookoutlet_service.forms import *
from bookoutlet_service.models import User
from bookoutlet_service.core.goodreads_api import get_user, get_bookshelf
from bookoutlet_service.core.goodreads_oauth import oauth_session, get_auth_url
from bookoutlet_service.core.bookoutlet import query_bookoutlet

# # TODO: add links


@app.route("/")
@app.route("/home")
def home():
    auth_url = get_auth_url(current_user)
    return render_template("home.html", title="Home", auth_url=auth_url)


@app.route("/register", methods=["GET", "POST"])
def register():
    # redirect to homepage if logged in
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RegistrationForm()

    if form.validate_on_submit():
        # hash user password using Bcrypt
        pw_hash = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(
            username=form.username.data, email=form.email.data, password=pw_hash
        )

        # update database with new user
        db.session.add(user)
        db.session.commit()

        flash(f"Account created!", "success")

        return redirect(url_for("login"))

    return render_template("register.html", title="Sign up!", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # login user
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash_msg = "Login Unsuccessful. Please check email and password"
            flash(flash_msg, "danger")

    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))  # do i want to redirect to login?


@app.route("/callback")
def callback():
    return render_template("callback.html", title="callback")


@app.route("/results")
def results():
    session = oauth_session(current_user)
    goodreads_user = get_user(session)
    member_id = goodreads_user[0]
    app.logger.info("member id retrieved: %s", member_id)

    start = time.time()
    books = get_bookshelf(member_id)
    matches = []
    for book in books:
        matches += query_bookoutlet(book)
    end = time.time()

    runtime = end - start
    app.logger.info("runtime %d", runtime)

    return render_template("results.html", title="results", matches=matches)


@app.route("/contact")
def contact():
    return render_template("contact.html", title="contact")


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()

        flash_msg = "Your account has been updated!"
        flash(flash_msg, "success")

        return redirect(url_for("account"))

    # display current username and email on form
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

    # default profile pic
    img_file = url_for("static", filename="images/default2.png")

    return render_template(
        "account.html", title="Update account", img_file=img_file, form=form
    )


def send_reset_email(user):
    token = user.get_reset_token()
    print("token {}".format(token))

    msg = Message(
        "Password Reset Request", sender="noreply@demo.com", recipients=[user.email]
    )
    msg.body = f"""We received a request to reset the password associated with\
the email address {user.email}. If you made this request, follow this link to\
reset your password:

{url_for('reset_token', token=token, _external=True)}

If you did not make this request, you can safely disregard this email.


Thanks,
The Team
"""
    print("MSG OBJ {}".format(msg))

    mail.send(msg)


@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)

        flash_msg = "An email has been sent with instructions to reset your \
                     password."
        flash(flash_msg, "info")

        return redirect(url_for("login"))

    return render_template("reset_request.html", title="Reset Password", form=form)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    user = User.verify_reset_token(token)

    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("reset_request"))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        pw_has = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = pw_has
        db.session.commit()

        flash_msg = "Your password has been updated! You can now log in."
        flash(flash_msg, "success")

        return redirect(url_for("login"))

    return render_template("reset_token.html", title="Reset Password", form=form)

