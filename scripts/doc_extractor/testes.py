from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
import os
import logging
from dotenv import load_dotenv
from langchain_qdrant import Qdrant
from langchain_openai import OpenAIEmbeddings
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = QdrantClient(url=QDRANT_URL, port="6333", api_key=QDRANT_API_KEY, timeout=10000)
collections = client.get_collections()

collection = client.get_collection("ga4-collection")
query = "quantos anos um cavalo vive?"
embedding_model = OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=OPENAI_API_KEY)
embbeded_query = embedding_model.embed_query(query)
result = client.search("ga4-collection", query_vector=embbeded_query,limit=1,with_payload=True)
print(result[0].payload["metadata"]["source"])

