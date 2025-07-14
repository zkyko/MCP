from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DeepSeek_api_key"),
    base_url=os.getenv("DeepSeek_api_base")
)

response = client.models.list()
print([model.id for model in response.data])
# This code lists all available models from the DeepSeek API using the OpenAI client.
# Ensure that the .env file contains the correct API key and base URL.