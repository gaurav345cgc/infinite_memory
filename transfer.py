from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import chromadb

# Step 1: MongoDB connection
mongo_url = "mongodb+srv://innovationcelleoxs19:AkMuA3cN2tsMllAx@cluster0.cywqo3w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
mongo_client = MongoClient(mongo_url)
db = mongo_client["test"]
messages_collection = db["messages"]

# Step 2: Load all documents
documents = list(messages_collection.find({}))

# Step 3: Prepare text, ids, metadata
texts, ids, metadatas = [], [], []

for doc in documents:
    content = doc.get("content", "").strip()
    if content:
        texts.append(content)
        ids.append(str(doc["_id"]))
        metadatas.append({
            "sender": doc.get("sender", ""),
            "threadId": str(doc.get("threadId", "")),
            "createdAt": str(doc.get("createdAt", ""))
        })

print(f"Loaded {len(texts)} documents for embedding.")

# Step 4: Embedding
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(texts).tolist()

# Step 5: New ChromaDB client (no Settings)
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="messages_collection")

# Optional: clear existing collection to avoid duplicates on rerun (uncomment if needed)
# collection.delete()

collection.add(documents=texts, embeddings=embeddings, ids=ids, metadatas=metadatas)

print("✅ ChromaDB import completed.")

# Step 6: Search query and user_id - make sure user_id matches exactly your data
query = "develop api in nodejs"
user_id = "user_2xdTnz6ZkFCbDxHWRMOzVY3XP6K"  # <-- fix if necessary

# Run query with filter on sender
results = collection.query(
    query_texts=[query],
    n_results=5,
    where={"sender": user_id}
)

# Step 7: Print results safely
if results and results["documents"] and results["documents"][0]:
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        print("\n---")
        print(f"Sender: {meta.get('sender', 'N/A')}")
        print(f"Thread: {meta.get('threadId', 'N/A')}")
        print(f"Created: {meta.get('createdAt', 'N/A')}")
        print(f"Content: {doc}")
else:
    print("No matches found for the query and sender filter.")
