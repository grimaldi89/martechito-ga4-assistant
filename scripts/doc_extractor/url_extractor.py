from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_qdrant import Qdrant
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from google.cloud import bigquery
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from error_wrapper import error_wrapper
import nest_asyncio
import logging
import datetime
import os
from google.auth import default


SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly',
          'https://www.googleapis.com/auth/bigquery',
          'https://www.googleapis.com/auth/drive.readonly'
          ]
credentials, project = default(scopes=SCOPES)
url_extractor_bp = Blueprint('url_extractor_bp', __name__)
load_dotenv()
nest_asyncio.apply()

PROJECT_NAME = os.getenv("PROJECT_NAME")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_PORT = os.getenv("QDRANT_PORT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATASET = os.getenv("DATASET")
TABLE = os.getenv("TABLE")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
CHUNK_SIZE = os.getenv("CHUNK_SIZE")
CHUNK_OVERLAP = os.getenv("CHUNK_OVERLAP")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")



if not all([PROJECT_NAME, QDRANT_API_KEY, QDRANT_URL, OPENAI_API_KEY,DATASET,TABLE,COLLECTION_NAME,EMBEDDING_MODEL,QDRANT_PORT,CHUNK_SIZE,CHUNK_OVERLAP]):
    logging.error("One or more environment variables are missing.")
    raise EnvironmentError("One or more environment variables are missing.")


embedding_client = OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=OPENAI_API_KEY)
qdrant_client = QdrantClient(url=QDRANT_URL, port=QDRANT_PORT, api_key=QDRANT_API_KEY)
vector_store = Qdrant(client=qdrant_client, collection_name=COLLECTION_NAME, embeddings=embedding_client)
bigquery_client = bigquery.Client(credentials=credentials, project=project)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@error_wrapper
def extract_urls(project_name,dataset, table):
    """
    Extracts URLs from a BigQuery dataset and table.

    Args:
        dataset (str): The name of the BigQuery dataset.
        table (str): The name of the BigQuery table.

    Returns:
        list: A list of dictionaries containing the extracted URLs, along with their corresponding subject and tool.
    """
    
    logging.info("Extracting Bigquery URL's...")
    query = f"SELECT url, tool, subject FROM `{project_name}.{dataset}.{table}`"
    query_job = bigquery_client.query(query)
    return [{"url": row.url, "subject": row.subject, "tool": row.tool} for row in query_job]
    
        

class CustomWebBaseLoader(WebBaseLoader):
    """
    A custom web base loader that extends the functionality of the WebBaseLoader class.

    Args:
        urls_with_metadata (list): A list of dictionaries containing URLs and corresponding metadata.

    Attributes:
        urls_with_metadata (list): A list of dictionaries containing URLs and corresponding metadata.

    Methods:
        load(): Loads the documents using the parent class's load method and adds additional metadata to each document.

    """

    def __init__(self, urls_with_metadata):
        super().__init__([item['url'] for item in urls_with_metadata])
        self.urls_with_metadata = urls_with_metadata

    def load(self):
        """
        Loads the documents using the parent class's load method and adds additional metadata to each document.

        Returns:
            list: A list of documents with added metadata.

        """
        documents = super().load()
        for doc, metadata in zip(documents, self.urls_with_metadata):
            doc.metadata['subject'] = metadata['subject']
            doc.metadata['tool'] = metadata['tool']
            doc.metadata["date"] = datetime.date.today().isoformat()
        return documents

@error_wrapper
def extract_documents(url_list_with_metadata):
    """
    Extracts documents from a list of URLs with metadata.

    Args:
        url_list_with_metadata (list): A list of URLs with metadata.

    Returns:
        data (list): A list of extracted documents.
    """
       
    logging.info("Extracting documents...")
    loader = CustomWebBaseLoader(url_list_with_metadata)
    data = loader.load()
    return data
    
    
    
@error_wrapper
def get_chunks(file):
    """
    Splits the given file into chunks using a text splitter.

    Args:
        file (str): The file to be split into chunks.

    Returns:
        list: A list of chunks obtained from the file.
    """
    logging.info("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", " ", ""],
            chunk_size=int(CHUNK_SIZE),
            chunk_overlap=int(CHUNK_OVERLAP),
            length_function=len
    )
    chunks = text_splitter.split_documents(file)
    return chunks
        
        
   
# Function to create a collection
@error_wrapper
def create_collection():
    """
    Creates a new collection in the qdrant_client.

    Parameters:
        None

    Returns:
        None
    """
    logging.info("Creating collection...")
    qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=int(CHUNK_SIZE), distance=Distance.COSINE),
    )
    return True    
        


       
@url_extractor_bp.route('/url_extractor',methods=["GET"])
@error_wrapper 
def main(request=request):
    url_list_with_metadata = extract_urls(PROJECT_NAME,DATASET, TABLE)   
    documents = extract_documents(url_list_with_metadata)
    chunks = get_chunks(documents)
    collection_exists = qdrant_client.collection_exists(COLLECTION_NAME)
    if not collection_exists:
        create_collection()
    vector_store.add_documents(chunks)
    logging.info("Documents added to vector store")
    return jsonify({"message": "Documents added to vector store"}), 200
    
if __name__ == '__main__':
    logging.info("Starting URL Extractor...")
    main()        

        
