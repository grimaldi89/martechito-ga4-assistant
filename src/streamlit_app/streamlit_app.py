from qdrant_client import QdrantClient
from langchain_qdrant import Qdrant
from langchain_openai import OpenAIEmbeddings , ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain , create_history_aware_retriever
from langchain_core.messages import HumanMessage
from langchain.globals import set_verbose
import os
import streamlit as st
from dotenv import load_dotenv
import logging

set_verbose(True)
logging.basicConfig(level=logging.INFO)
load_dotenv()

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_PORT = os.getenv("QDRANT_PORT")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
MODEL = os.getenv("MODEL")

if not all([QDRANT_API_KEY, QDRANT_URL, OPENAI_API_KEY, QDRANT_PORT, EMBEDDING_MODEL, COLLECTION_NAME, MODEL]):
        logging.error("One or more environment variables are missing.")
        raise EnvironmentError("One or more environment variables are missing.")


llm = ChatOpenAI(model_name=MODEL, temperature=0)

client = QdrantClient(url=QDRANT_URL, port=QDRANT_PORT, api_key=QDRANT_API_KEY)
embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=OPENAI_API_KEY)

vectorstore = Qdrant(
        client=client,
        collection_name=COLLECTION_NAME,
        embeddings=embeddings
)
retriever = vectorstore.as_retriever()

contextualize_q_system_prompt = """Given a chat history and the latest user question \
    which might reference context in the chat history, formulate a standalone question \
    which can be understood without the chat history. Do NOT answer the question, \
    just reformulate it if needed and otherwise return it as is.
    """
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

qa_system_prompt = """You are an AI agent called Martechito, working for a consultancy specialized in data, specifically GA4. 
    Your job is to answer questions for clients of this consultancy who license the product with them. 
    You need to be clear, didactic, detailed, and respectful in your responses. If you don’t know an answer, respectfully say that you don’t know. 
    Always respond to the client in the language used in the question. If the question is not related to GA4, you should not answer it. 
    All your responses need to be based on the context provided to you below:

    {context}

    If the provided context is not sufficient for the client’s question, say that you are unable to help them.
    """

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)


def main():
    """
    Main function for the Streamlit app.

    This function sets up the necessary components for the chatbot and handles user interactions.

    Returns:
        None
    """
   
    with st.sidebar:
        st.sidebar.markdown("<h1 style='text-align: center; margin-top: 0;'>Martechito</h1><h2 style='text-align: center; margin-top: 0;'>GA4 AI Assistant</h2>", unsafe_allow_html=True)
        st.sidebar.markdown("---")
        st.sidebar.markdown("""
            ### About
    This chatbot is a personal project created to answer questions about GA4, offering a conversational interface to its official documentation and public knowledge base.

    It leverages a Retrieval-Augmented Generation (RAG) model that integrates OpenAI's GPT-4 with a Qdrant vector store to provide relevant responses to user inquiries.

    Feedback and contributions are welcome! Feel free to reach out to me on [LinkedIn](https://www.linkedin.com/in/rodolfo-grimaldi/) or [GitHub](https://github.com/grimaldi89/martechito-ga4-assistant).
            """)
        st.sidebar.markdown("""
            ### Interactions
    The chatbot is designed to provide information about GA4, the latest version of Google Analytics. It can answer questions about GA4's features, implementation, and best practices.

    Ps: The chatbot is still in development, so it may not have all the answers you're looking for or may provide incorrect information. Please use it at your own discretion.
            """)
        # Adicionando imagens com links para LinkedIn e GitHub
        linkedin_url = "https://www.linkedin.com/in/rodolfo-grimaldi/"
        github_url = "https://github.com/grimaldi89/martechito-ga4-assistant"
        linkedin_image = "https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png"
        github_image = "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"

        st.markdown(f"<a href='{linkedin_url}'><img src='{linkedin_image}' style='height:50px; margin-right: 10px;'></a>"
                    f"<a href='{github_url}'><img src='{github_image}' style='height:50px;'></a>", unsafe_allow_html=True)
    with st.chat_message("assistant"):
        st.markdown("My name is Martechito, GA4 AI assistant, how can I help you today?")
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation" not in st.session_state:
        st.session_state.conversation = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Type your message here..."):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.conversation.append({"role": "user", "content": prompt})

        # Invoke QA model
        last_four_interactions = st.session_state.conversation[-4:]
        response = rag_chain.invoke({"input": prompt, "chat_history": last_four_interactions})
        logging.info(response)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response["answer"])
            st.session_state.conversation.extend([HumanMessage(content=prompt), response["answer"]])

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response["answer"]})


if __name__ == "__main__":
    main()