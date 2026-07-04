
import streamlit as st
import logging
import json
import threading
import uuid
import streamlit.components.v1 as components
from langchain_core.messages import HumanMessage
from agent import build_graph, estimate_cost
from analytics import log_login, log_interaction
from envs import LINKEDIN_URL, GITHUB_URL, LINKEDIN_IMAGE, GITHUB_IMAGE, OPENAI_API_KEY, SESSION_TOKEN_LIMIT

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
    if "usage" not in st.session_state:
        st.session_state.usage = {"input_tokens": 0, "output_tokens": 0, "search_calls": 0}


def extract_usage(result):
    message = result["messages"][-1]
    usage_metadata = getattr(message, "usage_metadata", None) or {}
    content = message.content if isinstance(message.content, list) else []
    search_calls = sum(
        1 for block in content
        if isinstance(block, dict) and block.get("type") == "web_search_call"
    )
    return usage_metadata.get("input_tokens", 0), usage_metadata.get("output_tokens", 0), search_calls


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


def get_graph(api_key):
    if st.session_state.get("graph_api_key") != api_key:
        st.session_state.graph = build_graph(api_key)
        st.session_state.graph_api_key = api_key
    return st.session_state.graph


def main():
    """
    Função principal para o aplicativo Streamlit.
    """
    setup_logging()
    setup_page()
    initialize_state()

    if not st.user.is_logged_in:
        _, center_col, _ = st.columns([1, 1.3, 1])
        with center_col:
            st.write("")
            st.write("")
            with st.container(border=True):
                _, logo_col, _ = st.columns([1, 1, 1])
                with logo_col:
                    st.image("src/img/martechito-logo.png", width="stretch")
                st.markdown(
                    "<h1 style='text-align:center; margin-bottom:0;'>Martechito</h1>"
                    "<p style='text-align:center; opacity:0.6; margin-top:0;'>GA4 AI Assistant</p>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    "<p style='text-align:center;'>Sign in with your Google account to get GA4 answers grounded in official documentation.</p>",
                    unsafe_allow_html=True,
                )
                st.write("")
                if st.button("Sign in with Google", type="primary", width="stretch"):
                    st.login()
        return

    if not st.session_state.get("login_logged"):
        user_info = {"email": st.user.email, "name": st.user.name, "picture": st.user.picture}
        threading.Thread(target=log_login, args=(user_info,), daemon=True).start()
        st.session_state["login_logged"] = True

    # Barra lateral
    with st.sidebar:
        st.caption(f"Signed in as {st.user.email}")
        if st.button("Log out"):
            st.logout()
        st.markdown("---")
        user_api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Only needed after the free session limit is reached. Your key is kept in this browser session only and is never stored."
        )
        usage = st.session_state.usage
        total_tokens = usage["input_tokens"] + usage["output_tokens"]
        free_tier_available = bool(OPENAI_API_KEY) and total_tokens < SESSION_TOKEN_LIMIT
        active_api_key = user_api_key or (OPENAI_API_KEY if free_tier_available else None)

        if user_api_key:
            st.caption(f"Tokens used this session: {total_tokens:,} ({usage['search_calls']} searches)")
            cost = estimate_cost(usage["input_tokens"], usage["output_tokens"], usage["search_calls"])
            if cost is not None:
                st.caption(f"Estimated cost: ${cost:.4f}")
        elif OPENAI_API_KEY:
            st.progress(min(total_tokens / SESSION_TOKEN_LIMIT, 1.0))
            st.caption(f"Free tier: {total_tokens:,}/{SESSION_TOKEN_LIMIT:,} tokens used this session")
        st.markdown("---")
        st.image("src/img/martechito-logo.png", width="stretch")
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
    if not active_api_key:
        if OPENAI_API_KEY:
            st.info("You've used up this session's free tokens. Please enter your own OpenAI API key in the sidebar to keep chatting.")
        else:
            st.info("Please enter your OpenAI API key in the sidebar to start chatting.")
        return

    if prompt := st.chat_input("Type your message here..."):

        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})

        # Invocar o agente
        try:
            graph = get_graph(active_api_key)
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            result = graph.invoke({"messages": [HumanMessage(content=prompt)]}, config=config)
            answer, sources = extract_answer_and_sources(result)
            input_tokens, output_tokens, search_calls = extract_usage(result)
            st.session_state.usage["input_tokens"] += input_tokens
            st.session_state.usage["output_tokens"] += output_tokens
            st.session_state.usage["search_calls"] += search_calls
        except Exception as e:
            logging.error(f"Agent call failed: {e}")
            with st.chat_message("assistant"):
                st.error("Something went wrong calling OpenAI — check that your API key is valid and has access to the configured model.")
            return

        if sources:
            answer = f"{answer} \n\n**Sources**:\n\n" + "\n\n".join(sources) + "\n"

        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

        user_info = {"email": st.user.email, "name": st.user.name, "picture": st.user.picture}
        threading.Thread(target=log_interaction, args=(user_info, prompt, answer), daemon=True).start()

        components.html(f"""
        <script>
          window.parent.parent.postMessage({{ type: 'prompt', prompt_data: {{'question':'{json.dumps(prompt)}','answer':'{json.dumps(answer)}'}} }}, '*');

        </script>
        """, height=0)

if __name__ == "__main__":
    main()
