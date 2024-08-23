
import streamlit as st
import logging
import json
import streamlit.components.v1 as components
from langchain_core.messages import HumanMessage
from langchain.globals import set_verbose
from llm_models import chain, llm, CONTEXTUALIZE_Q_SYSTEM_PROMPT
from vector_store_client import vectorstore
from envs import LINKEDIN_URL, GITHUB_URL, LINKEDIN_IMAGE, GITHUB_IMAGE

# Configurações iniciais
def setup_logging():
    set_verbose(True)
    logging.basicConfig(level=logging.INFO)

def setup_page():
    st.set_page_config(
        page_title="Martechito - GA4 AI Assistant",
        page_icon="img/robot.png",
        layout="centered",
        initial_sidebar_state="expanded",
        menu_items=None
    )

def initialize_state():
    if "show_custom_search" not in st.session_state:
        st.session_state.show_custom_search = False
        logging.info(st.session_state.show_custom_search)
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
        
def create_retriever():
    return vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"score_threshold": 0.5}
    )
    

def create_rag_chain(retriever,contextualize_q_system_prompt):
    return chain(retriever=retriever, llm=llm, contextualize_q_system_prompt=contextualize_q_system_prompt)


# Configuração de recuperação

def main():
    """
    Função principal para o aplicativo Streamlit.
    """
   
    
    
    
    setup_logging()
    setup_page()
    initialize_state()
    retriever = create_retriever()
    rag_chain = create_rag_chain(retriever,CONTEXTUALIZE_Q_SYSTEM_PROMPT)
   
    logging.info(st.session_state)
    
    # Barra lateral
    with st.sidebar:
        if st.button("Custom Vector Search"):
            st.session_state.show_custom_search = not st.session_state.show_custom_search

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
            rag_chain = chain(retriever=retriever, llm=llm, contextualize_q_system_prompt=CONTEXTUALIZE_Q_SYSTEM_PROMPT)
            
        st.image("img/martechito-removebg-preview.png", use_column_width=True)
        st.sidebar.markdown("<h2 style='text-align: center; margin-top: 0;'>GA4 AI Assistant</h2>", unsafe_allow_html=True)
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"""
            ### About
            This chatbot is a personal project created to answer questions about GA4, offering a conversational interface to its official documentation and public knowledge base.

            It leverages a Retrieval-Augmented Generation (RAG) model that integrates OpenAI's GPT-4 with a Qdrant vector store to provide relevant responses to user inquiries.

            Feedback and contributions are welcome! Feel free to reach out to me on [LinkedIn]({LINKEDIN_URL}) or [GitHub]({GITHUB_URL}).
        """)
        st.sidebar.markdown("""
            ### Interactions
            The chatbot is designed to provide information about GA4, the latest version of Google Analytics. It can answer questions about GA4's features, implementation and best practices.

            Ps: The chatbot is still in development, so it may not have all the answers you're looking for or may provide incorrect information. Please use it at your own discretion.
        """)
        
        st.markdown(f"<a href='{LINKEDIN_URL}'><img src='{LINKEDIN_IMAGE}' style='height:50px; margin-right: 10px;'></a>"
                    f"<a href='{GITHUB_URL}'><img src='{GITHUB_IMAGE}' style='height:50px;'></a>", unsafe_allow_html=True)
    
    with st.chat_message("assistant"):
        st.markdown("My name is Martechito, GA4 AI assistant, how can I help you today?")


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
        
        ##escaped_prompt = json.dumps(prompt)
        answer = response["answer"]
        components.html(f"""
        <script>
          window.parent.parent.postMessage({{ type: 'prompt', prompt_data: {{'question':'{json.dumps(prompt)}','answer':'{json.dumps(answer)}'}} }}, '*');
          
        </script>
        """, height=0)

if __name__ == "__main__":
    main()
