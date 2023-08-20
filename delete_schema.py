from dotenv import load_dotenv
import os
import weaviate

load_dotenv()

WEAVIATE_URL = os.getenv('WEAVIATE_URL')
WEAVIATE_API_KEY = os.getenv('WEAVIATE_API_KEY')

client = weaviate.Client(url=WEAVIATE_URL, auth_client_secret=weaviate.AuthApiKey(WEAVIATE_API_KEY))

# Function to delete the 'Chat' class
def delete_chat_class():
    try:
        client.schema.delete_all()
        print("Chat class deleted successfully")
    except weaviate.exceptions.WeaviateException as e:
        print(f"Error deleting Chat class: {str(e)}")

# Call the function to delete the class
delete_chat_class()
