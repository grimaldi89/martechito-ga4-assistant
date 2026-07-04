from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

from envs import MODEL, EMBEDDING_MODEL, OPENAI_API_KEY

llm = ChatOpenAI(model=MODEL, temperature=0)
embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """You are an AI agent called Martechito, working for a consultancy specialized in data, specifically GA4.
Your job is to answer questions for clients of this consultancy who license the product with them.
You need to be clear, didactic, detailed, and respectful in your responses. If you don't know an answer, respectfully say that you don't know.
Always respond to the client in the language used in the question. If the question is not related to GA4, you should not answer it.

You have a `search_ga4_docs` tool to look up relevant GA4 documentation. For any GA4-related question:
1. Call the tool before answering — do not rely on your own knowledge.
2. If the results don't sufficiently cover the question, call the tool again with a narrower or rephrased query (you may do this a couple of times).
3. All your responses must be grounded in the retrieved context. If, after searching, the context is still not sufficient for the client's question, say that you are unable to help them.
"""


def make_search_tool(retriever):
    @tool(response_format="content_and_artifact")
    def search_ga4_docs(query: str):
        """Search the GA4 documentation knowledge base for content relevant to the query."""
        docs = retriever.invoke(query)
        if not docs:
            return "No relevant documents found.", docs
        content = "\n\n".join(
            f"Source: {doc.metadata.get('title', doc.metadata.get('source', 'unknown'))}\n{doc.page_content}"
            for doc in docs
        )
        return content, docs

    return search_ga4_docs


def build_graph(retriever):
    search_tool = make_search_tool(retriever)
    llm_with_tools = llm.bind_tools([search_tool])

    def agent_node(state: MessagesState):
        messages = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode([search_tool]))
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")

    return graph.compile(checkpointer=MemorySaver())
