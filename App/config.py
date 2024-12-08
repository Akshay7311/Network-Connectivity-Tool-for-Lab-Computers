from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.account import Account
import os
from dotenv import load_dotenv

load_dotenv()
# Access environment variables

# Appwrite configuration
project_id = os.getenv('PROJECT_ID')
api_key = os.getenv('APP_WRITE_API_KEY')
client = Client()
client.set_endpoint('https://cloud.appwrite.io/v1')  # Set your Appwrite endpoint
client.set_project(project_id)  # Set your project ID
client.set_key(api_key)  # Set your API key

# Initialize Appwrite Database service
databases = Databases(client)
account = Account(client)

