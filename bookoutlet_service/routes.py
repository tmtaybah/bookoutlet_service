import time, re

from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

# local imports
from bookoutlet_service import app, db, bcrypt, mail, handler, celery
from bookoutlet_service.forms import *
from bookoutlet_service.models import User
from bookoutlet_service.core.goodreads_api import get_user, get_bookshelf
from bookoutlet_service.core.goodreads_oauth import GoodreadsClient
from bookoutlet_service.core.bookoutlet import query_bookoutlet


goodreads_client = GoodreadsClient()


@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        return bookoutlet_results()
    else:
        return render_template("home.html", title="Home", matches=[])


@app.route("/auth")
@login_required
def auth():
    auth_url = goodreads_client.authorize(current_user)
    return render_template("auth.html", title="Authorize", auth_url=auth_url)


@app.route("/register", methods=["GET", "POST"])
def register():
    # redirect to homepage if logged in
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RegistrationForm()

    if form.validate_on_submit():
        # check that I can clean profile url
        print(f"profile url = {form.goodreads_id.data}")

        # hash user password using Bcrypt
        pw_hash = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        goodreads_id = re.sub("[^0-9]", "", form.goodreads_id.data)
        print(f"CLEANED UP URL == {goodreads_id}")
        user = User(
            username=form.username.data,
            email=form.email.data,
            goodreads_id=goodreads_id,
            password=pw_hash,
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
        return redirect(url_for("main"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # login user
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash_msg = (
                "Login Unsuccessful. Please check the email and password you've entered"
            )
            flash(flash_msg, "danger")

    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    form = LoginForm()
    # resp = app.make_response(render_template("home.html"))
    resp = app.make_response(render_template("login.html", title="Login", form=form))
    resp.set_cookie("token", expires=0)
    return resp


@app.route("/callback")
def results():
    return bookoutlet_results()


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


def send_reset_email(user):
    token = user.get_reset_token()

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

    mail.send(msg)


def bookoutlet_results():

    session = goodreads_client.reuse_session(current_user)

    try:
        goodreads_user = get_user(session)
    except KeyError:
        auth_url = goodreads_client.authorize(current_user)
        return render_template("auth.html", title="Authorize", auth_url=auth_url)

    member_id = goodreads_user[0]
    app.logger.info("member id retrieved: %s", member_id)

    # check member id retrieved matches goodreads profile id
    goodreads_id = current_user.goodreads_id

    if member_id != goodreads_id:
        flash_msg = "A different user is currently already logged into Goodreads. Please log out of Goodreads and try again."
        flash(flash_msg, "danger")
        auth_url = get_auth_url(current_user)

        return render_template("auth.html", title="Authorize", auth_url=auth_url)

    start = time.time()

    books = get_bookshelf(member_id)
    matches = []
    for book in books:
        # check_bookoutlet.delay(book)
        matches += query_bookoutlet(book)

    end = time.time()

    runtime = end - start
    app.logger.info("runtime %d", runtime)

    return render_template("home.html", title="results", matches=matches)

