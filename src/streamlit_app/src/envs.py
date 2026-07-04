from dotenv import load_dotenv
import os
import logging

load_dotenv()

# Carregar variáveis de ambiente
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL")
LINKEDIN_URL = "https://www.linkedin.com/in/rodolfo-grimaldi/"
GITHUB_URL = "https://github.com/grimaldi89/martechito-ga4-assistant"
LINKEDIN_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png"
GITHUB_IMAGE = "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"

if not all([OPENAI_API_KEY, MODEL]):
    logging.error("One or more environment variables are missing.")
    raise EnvironmentError("One or more environment variables are missing.")
