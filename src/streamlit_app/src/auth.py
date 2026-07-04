from streamlit_google_auth import Authenticate

from envs import (
    GOOGLE_OAUTH_CLIENT_SECRETS_PATH,
    GOOGLE_OAUTH_REDIRECT_URI,
    GOOGLE_OAUTH_COOKIE_KEY,
)


def get_authenticator():
    return Authenticate(
        secret_credentials_path=GOOGLE_OAUTH_CLIENT_SECRETS_PATH,
        redirect_uri=GOOGLE_OAUTH_REDIRECT_URI,
        cookie_name="martechito_auth",
        cookie_key=GOOGLE_OAUTH_COOKIE_KEY,
        cookie_expiry_days=30,
    )
