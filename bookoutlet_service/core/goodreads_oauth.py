import os
import webbrowser, configparser

from rauth.service import OAuth1Service, OAuth1Session

from bookoutlet_service import db
from bookoutlet_service.models import User


""" goes through the oauth steps to establish an authenticated session
should create an authorization url where user will authorize or deny
application and redirects user to callback url.
returns a session object """

#  read API tokens
config = configparser.ConfigParser()
config.read("goodreads.env")
goodreads_key = config["goodreads"]["key"]
goodreads_secret = config["goodreads"]["secret"]

goodreads = OAuth1Service(
    consumer_key=goodreads_key,
    consumer_secret=goodreads_secret,
    name="goodreads",
    request_token_url="https://www.goodreads.com/oauth/request_token",
    authorize_url="https://www.goodreads.com/oauth/authorize",
    access_token_url="https://www.goodreads.com/oauth/access_token",
    base_url="https://www.goodreads.com/",
)


# write purpose of this function -- seems like for local testing purposes
def establish_session():

    # step 1 -- get request token
    request_token, request_token_secret = goodreads.get_request_token()

    # step 2 -- exchange request token for access token
    authorize_url = goodreads.get_authorize_url(request_token)
    print("Opening the following URL in your browser: " + authorize_url)
    print("Waiting for authorization...")
    webbrowser.open(authorize_url)

    # accepted = 'n'
    # while accepted.lower() == 'n':
    #     # you need to access the authorize_link via a browser,
    #     # and proceed to manually authorize the consumer
    #     accepted = input('Have you authorized me? (y/n)')

    # if the user has authorized access we can retrieve the access token
    # a session will be initiated
    session = goodreads.get_auth_session(request_token, request_token_secret)

    # we don't seem to be doing anything with these access tokens
    # ACCESS_TOKEN = session.access_token
    # ACCESS_TOKEN_SECRET = session.access_token_secret

    print("Success -- session established")
    return session


def get_auth_url(current_user):

    # get request token & exchange for auth url
    request_token, request_token_secret = goodreads.get_request_token()
    authorize_url = goodreads.get_authorize_url(request_token)

    # set current user data(?) & commit to db
    current_user.request_token = request_token
    current_user.request_secret = request_token_secret
    db.session.commit()

    return authorize_url


def oauth_session(current_user):

    print(f"CURRENT USER IS: {current_user}")
    # print("trying to see into user ... ", dir(current_user))

    request_token = current_user.request_token
    request_token_secret = current_user.request_secret
    # request_token, request_token_secret = goodreads.get_request_token()

    print(
        f"REQUEST TOKEN IS: {request_token} \nREQUEST TOKEN SECRET IS {request_token_secret}"
    )

    session = goodreads.get_auth_session(request_token, request_token_secret)
    access_token = session.access_token
    access_token_secret = session.access_token_secret

    print(
        f"ACCESS TOKEN IS: {access_token} \ACCESS TOKEN SECRET IS {access_token_secret}"
    )

    current_user.access_token = access_token
    current_user.access_secret = access_token_secret
    db.session.commit()

    return session


# checkout db for access tokens
# remove access tokens
