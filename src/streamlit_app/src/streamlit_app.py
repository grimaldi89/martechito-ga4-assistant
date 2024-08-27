
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
        page_icon="src/img/robot.png",
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
            
        st.image("src/img/martechito-logo.png", use_column_width=True)
        language = st.sidebar.selectbox("Select Language", ["Português","English"])
        # Conteúdo em inglês
        about_text_en = f"""
        ### About Martechito
        Martechito is a specialized chatbot designed to streamline your experience with GA4, the latest iteration of Google Analytics. As your digital assistant, Martechito provides instant, accurate responses directly from GA4's official documentation and public knowledge base.

        Powered by a state-of-the-art Retrieval-Augmented Generation (RAG) model, Martechito integrates OpenAI's GPT-4 with the Qdrant vector store to deliver contextually relevant answers to your inquiries.

        Your insights and suggestions are invaluable. Connect with us on [LinkedIn]({LINKEDIN_URL}) or via email at martechito.assistant@gmail.com to share your feedback or contribute to the project's growth.
        """

        interactions_text_en = """
        ### Interactions
        Martechito is equipped to assist you with GA4's features, implementation strategies, and best practices. Whether you're setting up GA4 for the first time or need expert advice on advanced configurations, Martechito is here to help.

        Please note: Martechito is currently in its MVP stage. While we strive for accuracy, some responses may be incomplete or require further refinement. We appreciate your understanding and encourage you to provide feedback via email at martechito.assistant@gmail.com to enhance its capabilities.
        """


        # Conteúdo em português
        about_text_pt = f"""
        ### Sobre o Martechito
        O Martechito é um chatbot especializado, projetado para simplificar sua experiência com o GA4, a versão mais recente do Google Analytics. Como seu assistente digital, o Martechito fornece respostas instantâneas e precisas diretamente da documentação oficial do GA4 e da base de conhecimento pública.

        Com a tecnologia de ponta do modelo de Geração Aumentada por Recuperação (RAG), o Martechito integra o GPT-4 da OpenAI com o armazenamento vetorial Qdrant para entregar respostas contextualmente relevantes às suas perguntas.

        Suas percepções e sugestões são inestimáveis. Conecte-se conosco no [LinkedIn]({LINKEDIN_URL}) ou via e-mail em martechito.assistant@gmail.com para compartilhar seu feedback ou contribuir para o crescimento do projeto.
        """

        interactions_text_pt = """
        ### Interações
        O Martechito está equipado para auxiliá-lo com os recursos, estratégias de implementação e melhores práticas do GA4. Seja para configurar o GA4 pela primeira vez ou para obter conselhos especializados sobre configurações avançadas, o Martechito está aqui para ajudar.

        Observe que o Martechito está atualmente em sua fase de MVP. Embora nos esforcemos para oferecer respostas precisas, algumas podem estar incompletas ou precisar de refinamento. Agradecemos sua compreensão e incentivamos você a fornecer feedback via e-mail em martechito.assistant@gmail.com para aprimorar suas capacidades.
        """

        st.sidebar.markdown("<h2 style='text-align: center; margin-top: 0;'>Martechito <br> GA4 Assistant</h2>", unsafe_allow_html=True)
        st.sidebar.markdown("---")
        if language == "English":
            st.sidebar.markdown(about_text_en)
            st.sidebar.markdown(interactions_text_en)
        else:
            st.sidebar.markdown(about_text_pt)
            st.sidebar.markdown(interactions_text_pt)

        st.sidebar.markdown("---")
        
        st.markdown(f"<a href='{LINKEDIN_URL}'><img src='{LINKEDIN_IMAGE}' style='height:50px; margin-right: 10px;'></a>"
                    , unsafe_allow_html=True)
    
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
