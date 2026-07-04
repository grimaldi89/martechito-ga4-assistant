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
LINKEDIN_URL = "https://www.linkedin.com/in/rodolfo-grimaldi/"
GITHUB_URL = "https://github.com/grimaldi89/martechito-ga4-assistant"
LINKEDIN_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png"
GITHUB_IMAGE = "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"

if not MODEL:
    logging.error("MODEL environment variable is missing.")
    raise EnvironmentError("MODEL environment variable is missing.")
