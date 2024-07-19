from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_qdrant import Qdrant
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from dotenv import load_dotenv
import nest_asyncio
import logging
import datetime
import os
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
nest_asyncio.apply()

def validate_env_variables():
    required_vars = [
        "QDRANT_API_KEY", "QDRANT_URL", "QDRANT_PORT",
        "OPENAI_API_KEY", "COLLECTION_NAME",
        "CHUNK_SIZE", "CHUNK_OVERLAP", "EMBEDDING_MODEL"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logging.error(f"Missing environment variables: {', '.join(missing_vars)}")
        raise EnvironmentError(f"Missing environment variables: {', '.join(missing_vars)}")
    else:
        logging.info("All environment variables are present.")

validate_env_variables()

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_PORT = os.getenv("QDRANT_PORT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

embedding_client = OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=OPENAI_API_KEY)
qdrant_client = QdrantClient(url=QDRANT_URL, port=QDRANT_PORT, api_key=QDRANT_API_KEY)
vector_store = Qdrant(client=qdrant_client, collection_name=COLLECTION_NAME, embeddings=embedding_client)

def extract_urls(list_name: str):
    with open(list_name) as f:
        documents = json.load(f)
    return documents
    
class CustomWebBaseLoader(WebBaseLoader):
   
    def __init__(self, urls_with_metadata):
        super().__init__([item['url'] for item in urls_with_metadata])
        self.urls_with_metadata = urls_with_metadata

    def load(self):
        
        documents = super().load()
        for doc, metadata in zip(documents, self.urls_with_metadata):
            doc.metadata['subject'] = metadata['subject']
            doc.metadata['tool'] = metadata['tool']
            doc.metadata["date"] = datetime.date.today().isoformat()
        return documents


def extract_documents(url_list_with_metadata: list):
    logging.info("Extracting documents...")
    loader = CustomWebBaseLoader(url_list_with_metadata)
    data = loader.load()
    return data
    
def get_chunks(documents: list):
    logging.info("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    return chunks

def create_collection():
    logging.info("Creating collection...")
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=CHUNK_SIZE, distance=Distance.COSINE),
    ) 
        
def main():
    try:
        logging.info("Starting URL Extractor...")
        urls = extract_urls("ga4_documents.json")
        documents = extract_documents(urls)
        chunks = get_chunks(documents)
        collection_exists = qdrant_client.collection_exists(COLLECTION_NAME)
        if not collection_exists:
            create_collection()
        vector_store.add_documents(chunks)
        logging.info("Documents added to vector store")
    except Exception as e:
        logging.error(e)
        raise e
    
if __name__ == '__main__':
    main()
   
    
    

        
