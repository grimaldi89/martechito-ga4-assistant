# <span style="color: orange;">Martechito</span> - GA4 Assistant

Martechito is an AI Assistant designed to help you find GA4 information efficiently. Acting as a knowledgeable companion, Martechito offers real-time assistance, code snippets, and deep dives into GA4's comprehensive documentation.

## Features

- **Interactive Chat Interface:** Engage in a lively conversation with Martechito. Ask anything from simple how-tos to complex GA4 queries. The assistant is equipped to understand and respond with relevant information, making the interaction both enriching and delightful.

- **Code Snippet Helper:** Martechito provides ready-to-use code snippets and SQL queries for GA4. This feature is particularly useful for beginners.

## Logic

Martechito is powered by an AI engine that uses a Retrieval-Augmented Generation (RAG) pipeline with GPT-4 and Qdrant vector store. This setup enables the assistant to dynamically retrieve and integrate information from a rich knowledge base, providing contextually relevant and accurate responses based on GA4 documentation.

The RAG pipeline enhances Martechito’s ability to understand and respond to user queries by leveraging the Qdrant vector store to provide up-to-date, context-aware advice. This system ensures that the interaction remains coherent and insightful, adapting to the context of each conversation.

## Setup Instructions

To get Martechito running on your local machine, follow these steps:

### Prerequisites

Before installation, you must:

- **Create an OpenAI API Key:** Instructions [here](https://platform.openai.com/api-keys).
- **Create a Qdrant Cluster:** Save the API Key and URL from the cluster. Instructions [here](https://qdrant.tech/documentation/cloud/quickstart-cloud/).
- **Install Python 3.10 or higher:** Instructions [here](https://www.python.org/downloads/).
- **Install Pip package manager:** Instructions [here](https://pip.pypa.io/en/stable/installation/).

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/grimaldi89/martechito-ga4-assistant.git
    ```

2. **Navigate to the project directory:**

    ```bash
    cd martechito-ga4-assistant/src/streamlit_app_local
    ```

3. **Create and activate a virtual environment (optional but recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

4. **Install the required packages (this may take a while):**

    ```bash
    pip install -r requirements.txt
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

1. **Extract and load the documents into the Qdrant cluster (this may take a while):**

    ```bash
    python3 load_qdrant_vector_db.py
    ```
    You should run this file only once, otherwise it will generate duplicated chunks in the DB.

2. **Start the Streamlit application:**

    ```bash
    streamlit run streamlit_app.py
    ```

    This will start the Streamlit server. You should see output indicating the local URL where the app is being served, typically `http://localhost:8501`.

## Using Martechito

Once Martechito is up and running, interact with it by typing your GA4-related queries into the chat interface and pressing send. Martechito will then provide insights, code snippets, or guidance based on your questions.

It’s important to note that the Qdrant settings and `ga4_documents.json` file can be customized to fit your specific needs. Please be aware that only a portion of the documents is mapped in the JSON file.

Check the sidebar for additional features and information that might enhance your experience with Martechito.

## Contributions

If you’d like to contribute to Martechito, please fork the repository and create a pull request with your features or fixes.

## License

Martechito is released under the [GNU License](LICENSE). See the `LICENSE` file for more details.
