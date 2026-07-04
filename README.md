# <span style="color: orange;">Martechito</span> - GA4 Assistant

Martechito is an AI Assistant designed to help you find GA4 information efficiently. Acting as a knowledgeable companion, Martechito offers real-time assistance, code snippets, and deep dives into GA4's comprehensive documentation.

## Features

- **Interactive Chat Interface:** Engage in a lively conversation with Martechito. Ask anything from simple how-tos to complex GA4 queries. The assistant is equipped to understand and respond with relevant information, making the interaction both enriching and delightful.

- **Code Snippet Helper:** Martechito provides ready-to-use code snippets and SQL queries for GA4. This feature is particularly useful for beginners.

## Logic

Martechito is powered by an **agentic pipeline** built with [LangGraph](https://langchain-ai.github.io/langgraph/) and OpenAI's native `web_search` tool (Responses API). Instead of maintaining a vector database, Martechito searches Google's official GA4 documentation live — the search is restricted to `support.google.com`, `developers.google.com`, and `marketingplatform.google.com` via the tool's domain filters, so it can't be grounded in random third-party pages. Every claim is expected to cite the page it came from (`url_citation` annotations returned by the API), which are surfaced as a "Sources" list under each answer so you can verify them yourself.

There is no ingestion pipeline, embeddings, or chunking to maintain — search results are fetched fresh on every question.

Conversation memory is kept per chat session via a LangGraph checkpointer, so follow-up questions retain context automatically.

If the deployer sets an `OPENAI_API_KEY`, each visitor gets a free trial covered by that key, capped at `SESSION_TOKEN_LIMIT` tokens (input + output) per browser session — after that, they must paste their own OpenAI API key into the sidebar to keep chatting, at their own cost. If `OPENAI_API_KEY` is left unset, every visitor has to bring their own key from the first message. A visitor's own key is kept only in their browser session — never written to disk or sent anywhere besides OpenAI.

Access to the app itself requires signing in with a Google account first (via [streamlit-google-auth](https://pypi.org/project/streamlit-google-auth/)) — nobody can reach the chat, free tier or not, without logging in.

## Setup Instructions

To get Martechito running on your local machine, follow these steps:

### Prerequisites

Before installation, you must:

- **Create an OpenAI API Key:** Instructions [here](https://platform.openai.com/api-keys). You'll paste this into the app's sidebar when it's running (see below) — the account needs access to a model that supports the Responses API `web_search` tool (e.g. `gpt-5.5`, `gpt-4.1`); plain `gpt-4o` does not support it.
- **Create a Google OAuth Client ID** (see "Google Sign-In" below) — required for anyone to be able to log in at all.
- **Install Python 3.10 or higher:** Instructions [here](https://www.python.org/downloads/).
- **Install Pip package manager:** Instructions [here](https://pip.pypa.io/en/stable/installation/).

### Google Sign-In

Martechito requires visitors to sign in with Google before they can chat. To set this up:

1. Go to the [Google Cloud Console credentials page](https://console.cloud.google.com/apis/credentials) for the project you want to use (can be the same project as your Firebase project).
2. If prompted, configure the **OAuth consent screen** first (External user type; add the `openid`, `.../auth/userinfo.email` and `.../auth/userinfo.profile` scopes).
3. Click **Create Credentials → OAuth client ID**, application type **Web application**.
4. Under **Authorized redirect URIs**, add every URL the app will be served from — at minimum `http://localhost:8501` for local testing, plus your production URL once deployed. This must match `GOOGLE_OAUTH_REDIRECT_URI` in your `.env` exactly.
5. Download the resulting JSON file, save it as `client_secret.json` inside `src/streamlit_app/` (next to `.env`) — **never commit this file** (it's already covered by `.gitignore`).
6. Generate a random secret for signing the login cookie: `python3 -c "import secrets; print(secrets.token_hex(32))"`.
7. Set `GOOGLE_OAUTH_CLIENT_SECRETS_PATH`, `GOOGLE_OAUTH_REDIRECT_URI`, and `GOOGLE_OAUTH_COOKIE_KEY` in your `.env` accordingly (see `.env.example`).

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/grimaldi89/martechito-ga4-assistant.git
    ```

2. **Navigate to the project directory:**

    ```bash
    cd martechito-ga4-assistant
    ```

3. **Create and activate a virtual environment (optional but recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

4. **Install the required packages (this may take a while):**

    ```bash
    pip install -r src/streamlit_app/requirements.txt
    ```

5. **Create a `.env` file based on the `.env.example`:**

    ```bash
    cp .env.example .env  # On Windows use `copy .env.example .env`
    ```

6. **Open the file in an editor, update the values, save, and close:**

    ```bash
    nano .env  # On Windows use `notepad .env`
    ```

### Running the Application

1. **Start the Streamlit application:**

    ```bash
    cd src/streamlit_app
    streamlit run src/streamlit_app.py
    ```

    This will start the Streamlit server. You should see output indicating the local URL where the app is being served, typically `http://localhost:8501`.

## Using Martechito

Once Martechito is up and running, sign in with your Google account, paste your OpenAI API key into the sidebar field if the free tier is exhausted (or unavailable), then interact with it by typing your GA4-related queries into the chat interface and pressing send. Martechito will then provide insights, code snippets, or guidance based on your questions, along with links to the official documentation it grounded its answer in.

Check the sidebar for additional features and information that might enhance your experience with Martechito.

## Contributions

If you’d like to contribute to Martechito, please fork the repository and create a pull request with your features or fixes.

## License

Martechito is released under the [GNU License](LICENSE). See the `LICENSE` file for more details.
