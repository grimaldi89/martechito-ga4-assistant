from dotenv import load_dotenv
import os
import logging

load_dotenv()

# Carregar variáveis de ambiente
MODEL = os.getenv("MODEL")
# Optional: the app owner's own key, used for each session's free tier.
# Once a session crosses SESSION_TOKEN_LIMIT, visitors must supply their own key.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SESSION_TOKEN_LIMIT = int(os.getenv("SESSION_TOKEN_LIMIT", "20000"))

# Google sign-in (required to use the app at all - see streamlit_google_auth)
GOOGLE_OAUTH_CLIENT_SECRETS_PATH = os.getenv("GOOGLE_OAUTH_CLIENT_SECRETS_PATH")
GOOGLE_OAUTH_REDIRECT_URI = os.getenv("GOOGLE_OAUTH_REDIRECT_URI")
GOOGLE_OAUTH_COOKIE_KEY = os.getenv("GOOGLE_OAUTH_COOKIE_KEY")

LINKEDIN_URL = "https://www.linkedin.com/in/rodolfo-grimaldi/"
GITHUB_URL = "https://github.com/grimaldi89/martechito-ga4-assistant"
LINKEDIN_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png"
GITHUB_IMAGE = "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"

REQUIRED_VARS = {
    "MODEL": MODEL,
    "GOOGLE_OAUTH_CLIENT_SECRETS_PATH": GOOGLE_OAUTH_CLIENT_SECRETS_PATH,
    "GOOGLE_OAUTH_REDIRECT_URI": GOOGLE_OAUTH_REDIRECT_URI,
    "GOOGLE_OAUTH_COOKIE_KEY": GOOGLE_OAUTH_COOKIE_KEY,
}
missing_vars = [name for name, value in REQUIRED_VARS.items() if not value]
if missing_vars:
    logging.error(f"Missing environment variables: {', '.join(missing_vars)}")
    raise EnvironmentError(f"Missing environment variables: {', '.join(missing_vars)}")
