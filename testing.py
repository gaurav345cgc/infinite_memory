from chromadb import PersistentClient
from loguru import logger
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import uuid
import random
import time
import os
import csv
from dotenv import load_dotenv
import openai

# --- Load env ---
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Config ---
CHROMA_PERSIST_PATH = "./chroma_perf_test"
USER_ID = "test_user_perf"
COLLECTION_NAME = f"{USER_ID}_collection"
USE_REAL_EMBEDDING = False  # ✅ Toggle to True for OpenAI test
EXPORT_LATENCY_CSV = True
TEST_DOCS = 1000
CONCURRENT_QUERIES = 100

# --- Setup Chroma ---
client = PersistentClient(path=CHROMA_PERSIST_PATH)
collection = client.get_or_create_collection(COLLECTION_NAME)

# --- Embedding functions ---
def generate_dummy_embedding(seed_text):
    random.seed(seed_text)
    return [random.random() for _ in range(1536)]

def generate_real_embedding(text):
    try:
        response = openai.Embedding.create(
            input=[text],
            model="text-embedding-3-large"
        )
        return response["data"][0]["embedding"]
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return generate_dummy_embedding(text)

def generate_embedding(text):
    return generate_real_embedding(text) if USE_REAL_EMBEDDING else generate_dummy_embedding(text)

# --- Data Loader ---
def populate_test_data(n=TEST_DOCS):
    logger.info(f"🟡 Populating {n} documents...")
    for i in tqdm(range(n), desc="Populating collection"):
        doc_id = str(uuid.uuid4())
        content = f"This is a test message #{i} about EOXS AI and vector DBs."
        embedding = generate_embedding(content)
        metadata = {
            "userId": USER_ID,
            "threadId": "test_thread",
            "messageId": doc_id,
            "createdAt": datetime.now().isoformat()
        }
        collection.add(
            documents=[content],
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[metadata]
        )
    logger.success("✅ Done populating test data.")

# --- Latency tests ---
def measure_latency(top_k=5):
    query = "Tell me more about EOXS AI and Gaurav's work."
    embedding = generate_embedding(query)
    start = time.perf_counter()
    results = collection.query(query_embeddings=[embedding], n_results=top_k)
    latency_ms = (time.perf_counter() - start) * 1000
    logger.info(f"⚡ Top-{top_k} query latency: {latency_ms:.2f} ms")
    logger.debug(f"📌 Sample result: {[doc[:60] for doc in results['documents'][0]]}")
    return latency_ms

def test_variable_top_k():
    latencies = []
    for k in [5, 10, 20, 50]:
        latency = measure_latency(top_k=k)
        latencies.append((k, latency))
    return latencies

# --- Concurrency test ---
def query_task(i):
    embedding = generate_embedding(f"Query {i}")
    start = time.perf_counter()
    collection.query(query_embeddings=[embedding], n_results=5)
    return (time.perf_counter() - start) * 1000

def run_concurrent_queries(q_count=CONCURRENT_QUERIES):
    logger.info(f"🚀 Running {q_count} concurrent queries...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        latencies = list(tqdm(executor.map(query_task, range(q_count)), total=q_count))

    logger.success(f"📈 Avg latency: {sum(latencies)/len(latencies):.2f} ms")
    logger.info(f"📉 Min latency: {min(latencies):.2f} ms")
    logger.info(f"📊 Max latency: {max(latencies):.2f} ms")
    return latencies

# --- Optional export ---
def export_latencies(topk_latencies, concurrent_latencies):
    filename = f"latency_report_{int(time.time())}.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Type", "Metric", "Latency (ms)"])
        for k, lat in topk_latencies:
            writer.writerow(["Top-K", f"Top-{k}", f"{lat:.2f}"])
        for idx, lat in enumerate(concurrent_latencies):
            writer.writerow(["Concurrent", f"Query-{idx+1}", f"{lat:.2f}"])
    logger.info(f"📁 Latencies exported to {filename}")

# --- Main ---
if __name__ == "__main__":
    populate_test_data(TEST_DOCS)
    topk_latencies = test_variable_top_k()
    concurrent_latencies = run_concurrent_queries(CONCURRENT_QUERIES)

    if EXPORT_LATENCY_CSV:
        export_latencies(topk_latencies, concurrent_latencies)
