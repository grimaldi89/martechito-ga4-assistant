from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_qdrant import Qdrant
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_community import GCSFileLoader
import os
import logging
from flask import Blueprint,request,jsonify
from dotenv import load_dotenv
from error_wrapper import error_wrapper

load_dotenv()
vectorizer_bp = Blueprint('vectorizer_bp', __name__)
logging.basicConfig(level=logging.INFO)

PROJECT_NAME = os.getenv("PROJECT_NAME")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_PORT = os.getenv("QDRANT_PORT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
CHUNK_SIZE = os.getenv("CHUNK_SIZE")
CHUNK_OVERLAP = os.getenv("CHUNK_OVERLAP")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

embbeding_client = OpenAIEmbeddings(model=EMBEDDING_MODEL)
qdrant_client = QdrantClient(url=QDRANT_URL, port=QDRANT_PORT, api_key=QDRANT_API_KEY)
vector_store = Qdrant(client=qdrant_client, collection_name=COLLECTION_NAME, embeddings=embbeding_client)

@error_wrapper
def get_chunks(file):
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=int(CHUNK_SIZE),
        chunk_overlap=int(CHUNK_OVERLAP),
        length_function=len
    )
    chunks = text_splitter.split_documents(file)
    return [chunk.page_content for chunk in chunks]

@error_wrapper
def create_collection():
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=int(CHUNK_SIZE), distance=Distance.COSINE),
    )
    return True
    
@vectorizer_bp.route('/vectorizer', methods=['POST'])
@error_wrapper
def main(cloud_event=request):
        
    cloud_event = cloud_event.get_json()
    bucket_name = cloud_event["bucket"]
    file_name = cloud_event["name"]
    loader = GCSFileLoader(project_name=PROJECT_NAME, bucket=bucket_name,blob=file_name)
    document = loader.load()
    collection_exists = qdrant_client.collection_exists(COLLECTION_NAME)
    if not collection_exists:
        create_collection()
    text = get_chunks(document)
    vector_store.add_texts(text)
    logging.info("Text chunks added to vector store")
    return jsonify({"message": "Sucesso!"}), 200
    

