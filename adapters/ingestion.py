from langchain.vectorstores import Weaviate
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from dotenv import load_dotenv
import os
load_dotenv()



WEAVIATE_URL = os.getenv('WEAVIATE_URL')
WEAVIATE_API_KEY = os.getenv('WEAVIATE_API_KEY')

def ingest_document(document_text):
    text_splitter = CharacterTextSplitter(chunk_size=250, chunk_overlap=100)
    docs = text_splitter.split_text(document_text)
    docs = [Document(page_content=t) for t in document_text]
    # Generate embeddings using OpenAIEmbeddings
    embeddings = OpenAIEmbeddings()
    Weaviate.from_documents(docs, embeddings, weaviate_url=WEAVIATE_URL, by_text=False)
    print('Ingestion Complete')
    return
