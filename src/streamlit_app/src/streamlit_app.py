
import streamlit as st
import logging
import json
import uuid
import streamlit.components.v1 as components
from langchain_core.messages import HumanMessage
from agent import build_graph
from envs import LINKEDIN_URL, GITHUB_URL, LINKEDIN_IMAGE, GITHUB_IMAGE

# Configurações iniciais
def setup_logging():
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
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())


def extract_answer_and_sources(result):
    content = result["messages"][-1].content
    if isinstance(content, str):
        return content, []

    answer_parts = []
    sources = []
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "text":
            answer_parts.append(block.get("text", ""))
            for annotation in block.get("annotations", []):
                if annotation.get("type") == "url_citation":
                    title = annotation.get("title") or annotation.get("url")
                    sources.append(f"[{title}]({annotation['url']})")

    return "".join(answer_parts), list(dict.fromkeys(sources))


def main():
    """
    Função principal para o aplicativo Streamlit.
    """
    setup_logging()
    setup_page()
    initialize_state()
    graph = build_graph()

    # Barra lateral
    with st.sidebar:
        st.image("src/img/martechito-logo.png", use_column_width=True)
        language = st.sidebar.selectbox("Select Language", ["English","Português"])
        # Conteúdo em inglês
        about_text_en = f"""
        ### About Martechito
        Martechito is a specialized chatbot designed to streamline your experience with GA4, the latest iteration of Google Analytics. As your digital assistant, Martechito provides instant, accurate responses directly from GA4's official documentation and public knowledge base.

        Powered by an agentic pipeline built on OpenAI's models, Martechito searches Google's official GA4 documentation live — deciding on its own when and what to search for — and grounds every answer in cited sources, instead of relying on a static knowledge base.

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

        Com um pipeline agentic sobre os modelos da OpenAI, o Martechito busca ao vivo na documentação oficial do GA4 — decidindo por conta própria quando e o que buscar — e fundamenta cada resposta em fontes citadas, em vez de depender de uma base de conhecimento estática.

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

        # Invocar o agente
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        result = graph.invoke({"messages": [HumanMessage(content=prompt)]}, config=config)
        answer, sources = extract_answer_and_sources(result)

        if sources:
            answer = f"{answer} \n\n**Sources**:\n\n" + "\n\n".join(sources) + "\n"

        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

        components.html(f"""
        <script>
          window.parent.parent.postMessage({{ type: 'prompt', prompt_data: {{'question':'{json.dumps(prompt)}','answer':'{json.dumps(answer)}'}} }}, '*');

        </script>
        """, height=0)

if __name__ == "__main__":
    main()
