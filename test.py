from langchain.vectorstores import Weaviate
from langchain.vectorstores import Weaviate
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from dotenv import load_dotenv
import os
load_dotenv()

WEAVIATE_URL = os.getenv('WEAVIATE_URL')
WEAVIATE_API_KEY = os.getenv('WEAVIATE_API_KEY')
import weaviate
client = weaviate.Client(url=WEAVIATE_URL, auth_client_secret=weaviate.AuthApiKey(WEAVIATE_API_KEY))


db = Weaviate(client=client, embedding=OpenAIEmbeddings())

retriever = db.as_retriever()

query = "Test"
docs = db.similarity_search_with_score(query, by_text=False)

print(docs)
