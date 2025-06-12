import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from logging_config import setup_logging

# Initialize logger
logger = setup_logging(__name__)

# Initialize ChromaDB client
persist_directory = os.getenv("CHROMA_PERSIST_PATH", "./chroma_persist")
logger.info(f"Initializing ChromaDB client with persist directory: {persist_directory}")
client = chromadb.PersistentClient(path=persist_directory)


def get_or_create_collection(user_id: str):
    """
    Retrieves or creates a ChromaDB collection for the given user_id.
    """
    collection_name = f"user_{user_id}_collection"
    try:
        collection = client.get_collection(name=collection_name)
        logger.debug(f"Retrieved existing collection: {collection_name}")
    except Exception:
        logger.debug(f"Collection {collection_name} not found. Creating new collection.")
        collection = client.create_collection(name=collection_name)
    return collection


def add_document(user_id: str, doc_id: str, embedding: List[float], metadata: Dict):
    """
    Adds or updates a document in the user's collection with metadata support.
    """
    logger.debug(f"Adding document to collection: user_id={user_id}, doc_id={doc_id}")
    
    if "content" not in metadata:
        logger.error("Missing 'content' in metadata")
        raise ValueError("metadata must include 'content' key")

    # Ensure threadId is preserved even if it's None
    if "threadId" not in metadata:
        metadata["threadId"] = None

    collection = get_or_create_collection(user_id)
    collection.upsert(
        documents=[metadata["content"]],
        metadatas=[metadata],
        ids=[doc_id],
        embeddings=[embedding]
    )
    logger.info(f"Document {doc_id} upserted successfully for user {user_id}.")


def query_similar(user_id: str, query_embedding: List[float], thread_id: str, metadata_filter: Optional[Dict[str, str]] = None, top_k: int = 5):
    """
    Queries for similar documents in the user's collection, filtered by threadId and optional metadata.
    """
    logger.debug(f"query_similar called with user_id={user_id}, thread_id={thread_id}, metadata_filter={metadata_filter}, top_k={top_k}")

    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError("user_id must be a non-empty string")
    if not isinstance(thread_id, str) or not thread_id.strip():
        raise ValueError("thread_id must be a non-empty string")
    if not (hasattr(query_embedding, "__iter__") and all(isinstance(x, (float, int)) for x in query_embedding)):
        raise ValueError("query_embedding must be an iterable of floats")

    collection = get_or_create_collection(user_id)
    
    # Build query filter with proper ChromaDB syntax
    if metadata_filter:
        # Combine multiple conditions with $and operator
        conditions = [{"threadId": thread_id}]
        for key, value in metadata_filter.items():
            conditions.append({key: value})
        query_filter = {"$and": conditions}
    else:
        query_filter = {"threadId": thread_id}

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=query_filter
    )

    logger.info(f"Query returned {len(results.get('documents', [[]])[0])} documents.")
    logger.debug(f"DB query results: {results}")
    return results


def query_similar_any_thread(user_id: str, query_embedding: List[float], metadata_filter: Optional[Dict[str, str]] = None, top_k: int = 5):
    """
    Queries for similar documents across all threads for the user, optionally filtered by metadata.
    """
    logger.debug(f"query_similar_any_thread called with user_id={user_id}, metadata_filter={metadata_filter}, top_k={top_k}")

    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError("user_id must be a non-empty string")
    if not (hasattr(query_embedding, "__iter__") and all(isinstance(x, (float, int)) for x in query_embedding)):
        raise ValueError("query_embedding must be an iterable of floats")

    collection = get_or_create_collection(user_id)

    # Build query filter with proper ChromaDB syntax
    if metadata_filter and len(metadata_filter) > 1:
        # Multiple conditions need $and operator
        conditions = []
        for key, value in metadata_filter.items():
            conditions.append({key: value})
        query_filter = {"$and": conditions}
    elif metadata_filter and len(metadata_filter) == 1:
        # Single condition, no need for $and
        key, value = list(metadata_filter.items())[0]
        query_filter = {key: value}
    else:
        query_filter = None  # No filter

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=query_filter
    )

    logger.info(f"Global query returned {len(results.get('documents', [[]])[0])} documents.")
    logger.debug(f"Global DB query results: {results}")
    return results
