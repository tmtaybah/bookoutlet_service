import os
import webbrowser, configparser

from rauth.service import OAuth1Service  # , OAuth1Session

from bookoutlet_service import db
from bookoutlet_service.models import User


""" goes through the oauth steps to establish an authenticated session
should create an authorization url where user will authorize or deny
application and redirects user to callback url.
returns a session object """


class GoodreadsClient:

    # read Goodreads API credentials from env file (https://www.goodreads.com/api)
    config = configparser.ConfigParser()
    config.read("goodreads.env")
    goodreads_key = config["goodreads"]["key"]
    goodreads_secret = config["goodreads"]["secret"]

    def __init__(self):
        self.goodreads = OAuth1Service(
            consumer_key=self.goodreads_key,
            consumer_secret=self.goodreads_secret,
            name="goodreads",
            request_token_url="https://www.goodreads.com/oauth/request_token",
            authorize_url="https://www.goodreads.com/oauth/authorize",
            access_token_url="https://www.goodreads.com/oauth/access_token",
            base_url="https://www.goodreads.com/",
        )

    def authorize(self, current_user):
        # get request token & exchange for auth url
        request_token, request_token_secret = self.goodreads.get_request_token()
        authorize_url = self.goodreads.get_authorize_url(request_token)

        # save request token to database
        current_user.request_token = request_token
        current_user.request_secret = request_token_secret
        db.session.commit()

        return authorize_url

    def new_session(self, current_user):

        # retrieve request token from database
        request_token = current_user.request_token
        request_token_secret = current_user.request_secret

        session = self.goodreads.get_auth_session(request_token, request_token_secret)

        # save access token to database
        current_user.access_token = session.access_token
        current_user.access_secret = session.access_token_secret
        db.session.commit()

        return session

    def reuse_session(self, current_user):

        session = self.goodreads.get_session(
            (current_user.access_token, current_user.access_secret)
        )

        return session

    # used for manual testing without current_user
    def establish_session():

        # step 1 -- get request token
        request_token, request_token_secret = goodreads.get_request_token()

        # step 2 -- exchange request token for access token
        authorize_url = goodreads.get_authorize_url(request_token)
        print("Opening the following URL in your browser: " + authorize_url)
        print("Waiting for authorization...")
        webbrowser.open(authorize_url)

        # if the user has authorized access we can retrieve the access token
        # a session will be initiated
        session = goodreads.get_auth_session(request_token, request_token_secret)
        print("Success -- session established")

        return session
