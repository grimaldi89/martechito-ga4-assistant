
from qdrant_client import QdrantClient
from langchain_qdrant import Qdrant
from envs import QDRANT_API_KEY, QDRANT_URL, QDRANT_PORT, COLLECTION_NAME
from llm_models import embeddings
client = QdrantClient(url=QDRANT_URL, port=QDRANT_PORT, api_key=QDRANT_API_KEY)


vectorstore = Qdrant(
    client=client,
    collection_name=COLLECTION_NAME,
    embeddings=embeddings
)
