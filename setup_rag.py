import os
import time

from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# Create a File Search store
store = client.file_search_stores.create(
    config={
        "display_name": "Automotive Sales Knowledge Base",
        "embedding_model": "models/gemini-embedding-2",
    }
)

print("Created File Search store:")
print(store.name)


# Upload documents
documents = [
    "knowledge/vehicle_catalog.txt",
    "knowledge/warranty_policy.txt",
]


for document in documents:

    print(f"\nUploading: {document}")

    operation = client.file_search_stores.upload_to_file_search_store(
        file_search_store_name=store.name,
        file=document,
    )

    while not operation.done:
        time.sleep(2)
        operation = client.operations.get(operation)

    print(f"Uploaded successfully: {document}")


print("\nRAG setup complete.")
print(f"\nAdd this to your .env file:\n")
print(f"GEMINI_FILE_SEARCH_STORE={store.name}")