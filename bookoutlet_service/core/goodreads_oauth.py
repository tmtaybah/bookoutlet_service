import os
import webbrowser

from rauth.service import OAuth1Service, OAuth1Session

from bookoutlet_service import db
from bookoutlet_service.models import User



''' goes through the oauth steps to establish an authenticated session
should create an authorization url where user will authorize or deny
application and redirects user to callback url.
returns a session object '''

goodreads = OAuth1Service(
        consumer_key=os.environ.get('GR_KEY'),
        consumer_secret=os.environ.get('GR_SECRET'),
        name='goodreads',
        request_token_url='https://www.goodreads.com/oauth/request_token',
        authorize_url='https://www.goodreads.com/oauth/authorize',
        access_token_url='https://www.goodreads.com/oauth/access_token',
        base_url='https://www.goodreads.com/'
    )


def establish_session():

    # step 1 -- get request token
    request_token, request_token_secret = goodreads.get_request_token()

    # step 2 -- exchange request token for access token
    authorize_url = goodreads.get_authorize_url(request_token)
    print('Opening the following URL in your browser: ' + authorize_url)
    print('Waiting authorization...')
    print(authorize_url)
    webbrowser.open(authorize_url)

    # accepted = 'n'
    # while accepted.lower() == 'n':
    #     # you need to access the authorize_link via a browser,
    #     # and proceed to manually authorize the consumer
    #     accepted = input('Have you authorized me? (y/n)')

    # if the user has authorized access we can retrieve the access token
    # a session will be initiated
    session = goodreads.get_auth_session(request_token, request_token_secret)

    ACCESS_TOKEN = session.access_token
    ACCESS_TOKEN_SECRET = session.access_token_secret

    print('Success -- session established')
    return session


def get_auth_url(current_user):
    # step 1 -- get request token
    request_token, request_token_secret = goodreads.get_request_token()
    authorize_url = goodreads.get_authorize_url(request_token)

    current_user.request_token = request_token
    current_user.request_secret = request_token_secret
    db.session.commit()

    return authorize_url


def oauth_session(current_user):

    request_token = current_user.request_token
    request_token_secret = current_user.request_secret

    session = goodreads.get_auth_session(request_token, request_token_secret)
    access_token = session.access_token
    access_token_secret = session.access_token_secret

    current_user.access_token = access_token
    current_user.access_secret = access_token_secret
    db.session.commit()

    return session
