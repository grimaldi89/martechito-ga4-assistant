
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from envs import MODEL, QDRANT_API_KEY, QDRANT_URL, QDRANT_PORT, EMBEDDING_MODEL, OPENAI_API_KEY

llm = ChatOpenAI(model_name=MODEL, temperature=0)
embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=OPENAI_API_KEY)
CONTEXTUALIZE_Q_SYSTEM_PROMPT = """Given a chat history and the latest user question \
    which might reference context in the chat history, formulate a standalone question \
    which can be understood without the chat history. Do NOT answer the question, \
    just reformulate it if needed and otherwise return it as is.
    """

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