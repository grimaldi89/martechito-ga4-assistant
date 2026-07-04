
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from envs import QDRANT_API_KEY, QDRANT_URL, QDRANT_PORT, COLLECTION_NAME
from agent import embeddings

client = QdrantClient(url=QDRANT_URL, port=QDRANT_PORT, api_key=QDRANT_API_KEY)

vectorstore = QdrantVectorStore(
    client=client,
    collection_name=COLLECTION_NAME,
    embedding=embeddings
)


def get_retriever(search_type="similarity_score_threshold", search_kwargs=None):
    return vectorstore.as_retriever(
        search_type=search_type,
        search_kwargs=search_kwargs or {"score_threshold": 0.5}
    )
