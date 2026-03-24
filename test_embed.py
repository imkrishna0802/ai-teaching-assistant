import os
from google import genai

api_key = os.environ["GOOGLE_API_KEY"]
client = genai.Client(api_key=api_key)

r = client.models.embed_content(
    model="models/text-embedding-004",
    requests=[{"content": "hello world"}]
)

print(len(r.embeddings[0].values))