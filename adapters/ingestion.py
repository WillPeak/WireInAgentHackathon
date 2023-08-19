from langchain.document_loaders import TextLoader
from langchain.vectorstores import Weaviate
from langchain.embeddings import OpenAIEmbeddings
import weaviate
from dotenv import load_dotenv
import os
load_dotenv()



WEAVIATE_URL = os.getenv('WEAVIATE_URL')
WEAVIATE_API_KEY = os.getenv('WEAVIATE_API_KEY')

def ingest_document(document_text, index_name):
    # Create a document object from the given text
    documents = [TextLoader.from_text(document_text)]
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)
    Weaviate.from_documents(docs, embeddings, weaviate_url=WEAVIATE_URL, by_text=False)


    # Generate embeddings using OpenAIEmbeddings
    embeddings_model = OpenAIEmbeddings()
    embeddings = [embeddings_model.encode(doc.text) for doc in documents]

    # Initialize Weaviate vector store
    vectorstore = Weaviate.from_documents(documents, embeddings, client=client, by_text=False)

    # Ingest into Weaviate
    vectorstore.ingest(index_name=index_name)

    print('Ingestion Complete')
