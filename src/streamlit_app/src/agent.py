from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, END

from envs import MODEL

ALLOWED_DOMAINS = [
    "support.google.com",
    "developers.google.com",
    "marketingplatform.google.com",
]

# Standard-tier per-1M-token pricing (USD). Only models we've verified pricing
# for are listed; unlisted models fall back to "no cost estimate available".
MODEL_PRICING = {
    "gpt-5.5": {"input_per_1m": 5.00, "output_per_1m": 30.00},
}
WEB_SEARCH_CALL_PRICE = 0.01


def estimate_cost(input_tokens: int, output_tokens: int, search_calls: int):
    pricing = MODEL_PRICING.get(MODEL)
    if not pricing:
        return None
    return (
        (input_tokens / 1_000_000) * pricing["input_per_1m"]
        + (output_tokens / 1_000_000) * pricing["output_per_1m"]
        + search_calls * WEB_SEARCH_CALL_PRICE
    )

SYSTEM_PROMPT = f"""You are an AI agent called Martechito, working for a consultancy specialized in data, specifically GA4.
Your job is to answer questions for clients of this consultancy who license the product with them.
You need to be clear, didactic, detailed, and respectful in your responses. If you don't know an answer, respectfully say that you don't know.
Always respond to the client in the language used in the question. If the question is not related to GA4, you should not answer it.

You have a web search tool, restricted to {", ".join(ALLOWED_DOMAINS)}. For any GA4-related question:
1. Always search before answering — do not rely on your own knowledge.
2. If the results don't sufficiently cover the question, search again with a narrower or rephrased query.
3. Ground every claim in the retrieved pages and cite them. If, after searching, you still can't find enough to answer, say that you are unable to help them rather than guessing.
"""


def build_graph(api_key: str):
    llm = ChatOpenAI(model=MODEL, temperature=0, api_key=api_key)
    llm_with_search = llm.bind_tools([
        {"type": "web_search", "filters": {"allowed_domains": ALLOWED_DOMAINS}}
    ])

    def agent_node(state: MessagesState):
        messages = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
        response = llm_with_search.invoke(messages)
        return {"messages": [response]}

    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent_node)
    graph.set_entry_point("agent")
    graph.add_edge("agent", END)

    return graph.compile(checkpointer=MemorySaver())
