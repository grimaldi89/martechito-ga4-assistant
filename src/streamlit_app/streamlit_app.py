import os
import streamlit as st
import streamlit.components.v1 as components
import logging
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from langchain_qdrant import Qdrant
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain_core.messages import HumanMessage
from langchain.globals import set_verbose

# Configurações iniciais
set_verbose(True)
logging.basicConfig(level=logging.INFO)
load_dotenv()

# Carregar variáveis de ambiente
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

# Configuração dos modelos
llm = ChatOpenAI(model_name=MODEL, temperature=0)
client = QdrantClient(url=QDRANT_URL, port=QDRANT_PORT, api_key=QDRANT_API_KEY)
embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=OPENAI_API_KEY)

vectorstore = Qdrant(
    client=client,
    collection_name=COLLECTION_NAME,
    embeddings=embeddings
)

# Função para criar a cadeia de recuperação
def chain(retriever, llm, contextualize_q_system_prompt):
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
        VERY IMPORTANT: ALL THE RESPONSES SHOULD BE BASED ON THE CONTEXT PROVIDED TO YOU BELOW. IF THE CONTEXT IS NOT SUFFICIENT FOR THE CLIENT'S QUESTION, SAY THAT YOU ARE UNABLE TO HELP THEM.
        """

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    return rag_chain

# Configuração de recuperação
contextualize_q_system_prompt = """Given a chat history and the latest user question \
    which might reference context in the chat history, formulate a standalone question \
    which can be understood without the chat history. Do NOT answer the question, \
    just reformulate it if needed and otherwise return it as is.
    """

def main():
    """
    Função principal para o aplicativo Streamlit.
    """
    # Inicialize o retriever padrão
    retriever = vectorstore.as_retriever(search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.5})
    rag_chain = chain(retriever=retriever, llm=llm, contextualize_q_system_prompt=contextualize_q_system_prompt)
    st.set_page_config(page_title="Martechito - GA4 AI Assistant", page_icon="robot.png", layout="centered", initial_sidebar_state="expanded", menu_items=None)
    logging.info(st.session_state)


    # Inicialize o estado para o "Custom Search"
    if "show_custom_search" not in st.session_state:
        st.session_state.show_custom_search = False
        logging.info(st.session_state.show_custom_search)

    

    # Barra lateral
    with st.sidebar:
        if st.button("Custom Vector Search"):
            st.session_state.show_custom_search = not st.session_state.show_custom_search
            logging.info(st.session_state.show_custom_search)

    # Exibir opções somente se "Custom Search" estiver ativo
        if st.session_state.show_custom_search:
            option = st.selectbox("Select a search method", ["Similarity Score Threshold", "MMR"])
            if option == "Similarity Score Threshold":
                score_threshold = st.slider("Select a similarity score threshold", 0.0, 1.0, value=0.5)
                retriever = vectorstore.as_retriever(search_type="similarity_score_threshold", search_kwargs={"score_threshold": score_threshold})
            elif option == "MMR":
                k = st.slider("Select a number of results", 1, 10, value=6)
                lambda_mult = st.slider("Select a lambda multiplier", 0.0, 1.0, value=0.25)
                retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={'k': k, 'lambda_mult': lambda_mult})
        # Atualize o rag_chain com o novo retriever
            rag_chain = chain(retriever=retriever, llm=llm, contextualize_q_system_prompt=contextualize_q_system_prompt)
            
        st.image("martechito-removebg-preview.png", use_column_width=True)
        st.sidebar.markdown("<h2 style='text-align: center; margin-top: 0;'>GA4 AI Assistant</h2>", unsafe_allow_html=True)
        st.sidebar.markdown("---")
        st.sidebar.markdown("""
            ### About
            This chatbot is a personal project created to answer questions about GA4, offering a conversational interface to its official documentation and public knowledge base.

            It leverages a Retrieval-Augmented Generation (RAG) model that integrates OpenAI's GPT-4 with a Qdrant vector store to provide relevant responses to user inquiries.

            Feedback and contributions are welcome! Feel free to reach out to me on [LinkedIn](https://www.linkedin.com/in/rodolfo-grimaldi/) or [GitHub](https://github.com/grimaldi89/martechito-ga4-assistant).
        """)
        st.sidebar.markdown("""
            ### Interactions
            The chatbot is designed to provide information about GA4, the latest version of Google Analytics. It can answer questions about GA4's features, implementation and best practices.

            Ps: The chatbot is still in development, so it may not have all the answers you're looking for or may provide incorrect information. Please use it at your own discretion.
        """)
        linkedin_url = "https://www.linkedin.com/in/rodolfo-grimaldi/"
        github_url = "https://github.com/grimaldi89/martechito-ga4-assistant"
        linkedin_image = "https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png"
        github_image = "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"

        st.markdown(f"<a href='{linkedin_url}'><img src='{linkedin_image}' style='height:50px; margin-right: 10px;'></a>"
                    f"<a href='{github_url}'><img src='{github_image}' style='height:50px;'></a>", unsafe_allow_html=True)
    with st.chat_message("assistant"):
        st.markdown("My name is Martechito, GA4 AI assistant, how can I help you today?")

    # Inicializar histórico de mensagens
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation" not in st.session_state:
        st.session_state.conversation = []

    # Exibir histórico de mensagens no app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Reagir à entrada do usuário
    if prompt := st.chat_input("Type your message here..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.conversation.append({"role": "user", "content": prompt})
        components.html(f"<script>parent.window.dataLayer = parent.window.dataLayer || []; parent.window.dataLayer.push({{'event':'send_question','prompt':'{prompt}'}});</script>")

        # Invocar o modelo QA
        last_four_interactions = st.session_state.conversation[-4:]
        response = rag_chain.invoke({"input": prompt, "chat_history": last_four_interactions})
        sources = list(set([f"[{doc.metadata['title']}]({doc.metadata['source']})" for doc in response["context"]]))
        if sources:
            response["answer"] = f"{response['answer']} \n\n**Sources**:\n\n" + "\n\n".join(sources) + "\n"

        with st.chat_message("assistant"):
            st.markdown(response["answer"])
        st.session_state.conversation.extend([HumanMessage(content=prompt), response["answer"]])
        st.session_state.messages.append({"role": "assistant", "content": response["answer"]})

if __name__ == "__main__":
    main()
