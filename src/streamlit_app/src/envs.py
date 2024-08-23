from dotenv import load_dotenv
import os
import logging

load_dotenv()

# Carregar variáveis de ambiente
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_PORT = os.getenv("QDRANT_PORT")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
MODEL = os.getenv("MODEL")
LINKEDIN_URL = "https://www.linkedin.com/in/rodolfo-grimaldi/"
GITHUB_URL = "https://github.com/grimaldi89/martechito-ga4-assistant"
LINKEDIN_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png"
GITHUB_IMAGE = "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"

if not all([QDRANT_API_KEY, QDRANT_URL, OPENAI_API_KEY, QDRANT_PORT, EMBEDDING_MODEL, COLLECTION_NAME, MODEL]):
    logging.error("One or more environment variables are missing.")
    raise EnvironmentError("One or more environment variables are missing.")