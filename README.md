# <span style="color: orange;">Martechito</span> - GA4 Assistant

Martechito is an AI Assistant designed to help you find GA4 information efficiently. Acting as a knowledgeable companion, Martechito offers real-time assistance, code snippets, and deep dives into GA4's comprehensive documentation.

## Features

- **Interactive Chat Interface:** Engage in a lively conversation with Martechito. Ask anything from simple how-tos to complex GA4 queries. The assistant is equipped to understand and respond with relevant information, making the interaction both enriching and delightful.

- **Code Snippet Helper:** Martechito provides ready-to-use code snippets and SQL queries for GA4. This feature is particularly useful for beginners.

## Logic

Martechito is powered by an **agentic pipeline** built with [LangGraph](https://langchain-ai.github.io/langgraph/) and OpenAI's native `web_search` tool (Responses API). Instead of maintaining a vector database, Martechito searches Google's official GA4 documentation live — the search is restricted to `support.google.com`, `developers.google.com`, and `marketingplatform.google.com` via the tool's domain filters, so it can't be grounded in random third-party pages. Every claim is expected to cite the page it came from (`url_citation` annotations returned by the API), which are surfaced as a "Sources" list under each answer so you can verify them yourself.

There is no ingestion pipeline, embeddings, or chunking to maintain — search results are fetched fresh on every question.

Conversation memory is kept per chat session via a LangGraph checkpointer, so follow-up questions retain context automatically.

Each visitor enters their own OpenAI API key directly in the app's sidebar — it's kept only in their browser session (never written to disk or sent anywhere besides OpenAI), so whoever deploys Martechito doesn't need to fund everyone else's usage.

## Setup Instructions

To get Martechito running on your local machine, follow these steps:

### Prerequisites

Before installation, you must:

- **Create an OpenAI API Key:** Instructions [here](https://platform.openai.com/api-keys). You'll paste this into the app's sidebar when it's running (see below) — the account needs access to a model that supports the Responses API `web_search` tool (e.g. `gpt-5.5`, `gpt-4.1`); plain `gpt-4o` does not support it.
- **Install Python 3.10 or higher:** Instructions [here](https://www.python.org/downloads/).
- **Install Pip package manager:** Instructions [here](https://pip.pypa.io/en/stable/installation/).

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

Once Martechito is up and running, paste your OpenAI API key into the sidebar field, then interact with it by typing your GA4-related queries into the chat interface and pressing send. Martechito will then provide insights, code snippets, or guidance based on your questions, along with links to the official documentation it grounded its answer in.

Check the sidebar for additional features and information that might enhance your experience with Martechito.

## Contributions

If you’d like to contribute to Martechito, please fork the repository and create a pull request with your features or fixes.

## License

Martechito is released under the [GNU License](LICENSE). See the `LICENSE` file for more details.
