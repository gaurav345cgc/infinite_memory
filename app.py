import os
import time
import uuid
from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from models import EmbedRequest, EmbedResponse, AIResponseRequest, AIResponseResponse, QueryRequest, QueryResponse, QueryMatch
from embedding import generate_embedding
from db import add_document, query_similar_any_thread, get_or_create_collection
from utils import current_utc_timestamp
from openai import OpenAI, OpenAIError
from logging_config import setup_logging
from monitoring import log_api_call, get_api_stats, get_average_latency, latency_collection

# Initialize logger
logger = setup_logging(__name__)

app = FastAPI(title="EOXS AI Embedding Microservice")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monitoring middleware
@app.middleware("http")
async def monitor_api_calls(request: Request, call_next):
    start_time = time.time()
    
    # Extract request data
    endpoint = request.url.path
    user_id = None
    message_id = None
    thread_id = None
    query = None
    
    # Try to extract data from request body for specific endpoints
    if endpoint in ["/embed", "/rag-context", "/rag-generate", "/query"]:
        try:
            body = await request.body()
            if body:
                import json
                request_data = json.loads(body)
                user_id = request_data.get("userId")
                message_id = request_data.get("messageId")
                thread_id = request_data.get("threadId")
                query = request_data.get("query")
        except:
            pass
    
    # Process the request
    try:
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000
        status = "success" if response.status_code < 400 else "failure"
        error = None if response.status_code < 400 else f"HTTP {response.status_code}"
        
        # Log the API call
        log_api_call(
            endpoint=endpoint,
            user_id=user_id,
            message_id=message_id,
            thread_id=thread_id,
            query=query,
            duration_ms=duration_ms,
            status=status,
            error=error
        )
        
        return response
        
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        error_msg = str(e)
        
        # Log the failed API call
        log_api_call(
            endpoint=endpoint,
            user_id=user_id,
            message_id=message_id,
            thread_id=thread_id,
            query=query,
            duration_ms=duration_ms,
            status="failure",
            error=error_msg
        )
        
        raise

# OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
logger.info(f"OPENAI_API_KEY: {openai_api_key}")
if not openai_api_key:
    logger.error("OPENAI_API_KEY environment variable not set")
    raise RuntimeError("OPENAI_API_KEY environment variable not set")

client = OpenAI(api_key=openai_api_key)
logger.info("OpenAI client initialized")


@app.post("/embed", response_model=EmbedResponse)
async def embed_message(req: EmbedRequest) -> EmbedResponse:
    try:
        logger.info(f"Embed request: user={req.userId}, message={req.messageId}")
        embedding_vector = generate_embedding(req.content)

        metadata = {
            "userId": req.userId,
            "messageId": req.messageId,
            "content": req.content,
            "createdAt": current_utc_timestamp(),
            "threadId": req.threadId or None,
            "type": "user_message",  # Mark this as a user message
        }
        
        # Add any additional metadata from the request
        if req.metadata:
            metadata.update(req.metadata)

        add_document(req.userId, req.messageId, embedding_vector, metadata)
        return EmbedResponse()
    except Exception as e:
        logger.error(f"Error embedding message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to embed message")


@app.post("/embed-ai-response", response_model=AIResponseResponse)
async def embed_ai_response(req: AIResponseRequest) -> AIResponseResponse:
    try:
        logger.info(f"Embed AI response: user={req.userId}, response={req.responseId}")
        embedding_vector = generate_embedding(req.content)

        metadata = {
            "userId": req.userId,
            "responseId": req.responseId,
            "userMessageId": req.userMessageId,
            "content": req.content,
            "createdAt": current_utc_timestamp(),
            "threadId": req.threadId or None,
            "type": "ai_response",  # Mark this as an AI response
            "context": req.context or None,
        }
        
        # Add any additional metadata from the request
        if req.metadata:
            metadata.update(req.metadata)

        add_document(req.userId, req.responseId, embedding_vector, metadata)
        return AIResponseResponse()
    except Exception as e:
        logger.error(f"Error embedding AI response: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to embed AI response")


@app.post("/rag-context")
async def get_rag_context(req: QueryRequest, similarity_threshold: float = 0):
    """
    RAG Phase 1: Retrieve similar messages as plain text context.
    """
    try:
        logger.info(f"RAG context request: userId={req.userId}, filters={req.filters}, query={req.query}, threshold={similarity_threshold}")
        query_text = req.query[0] if isinstance(req.query, list) else req.query

        if not isinstance(query_text, str):
            raise HTTPException(status_code=400, detail="Invalid query type")

        query_embedding = generate_embedding(query_text)

        where_filter = {}

        if req.threadId:
            where_filter["threadId"] = req.threadId

        if req.filters:
            where_filter.update(req.filters)

        # Add filter to exclude AI responses and query-like content
        where_filter["type"] = "user_message"

        results = query_similar_any_thread(req.userId, query_embedding, metadata_filter=where_filter, top_k=10)
        documents = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]
        
        # Apply threshold filtering and query similarity filtering
        relevant_documents = []
        relevant_scores = []
        relevant_count = 0
        query_lower = query_text.lower().strip()
        
        for doc, dist in zip(documents, distances):
            similarity_score = 1 - dist  # Convert distance to similarity
            doc_lower = doc.lower().strip()
            
            # Only skip if document is exactly the same as the query
            if (similarity_score >= similarity_threshold and 
                doc_lower != query_lower):
                relevant_documents.append(doc)
                relevant_scores.append(round(similarity_score, 4))
                relevant_count += 1
        
        # Return filtered documents
        context = "\n---\n".join(relevant_documents) if relevant_documents else ""
        
        logger.info(f"Returning {relevant_count}/{len(documents)} documents for context (threshold: {similarity_threshold})")
        
        return {
            "context": context,
            "totalFound": len(documents),
            "relevantCount": relevant_count,
            "threshold": similarity_threshold,
            "similarityScores": relevant_scores if relevant_scores else []
        }
    except Exception as e:
        logger.exception(f"Error building RAG context: {e}")
        raise HTTPException(status_code=500, detail="Failed to build context")


@app.post("/rag-generate")
async def rag_generate(req: QueryRequest = Body(...)):
    """
    RAG Phase 2: Retrieve context and generate response.
    """
    try:
        logger.info(f"RAG generate request: userId={req.userId}, filters={req.filters}, query={req.query}")
        query_text = req.query[0] if isinstance(req.query, list) else req.query

        if not isinstance(query_text, str):
            raise HTTPException(status_code=400, detail="Invalid query type")

        query_embedding = generate_embedding(query_text)

        where_filter = {}

        if req.threadId:
            where_filter["threadId"] = req.threadId

        if req.filters:
            where_filter.update(req.filters)

        # Add filter to exclude AI responses and query-like content
        where_filter["type"] = "user_message"

        results = query_similar_any_thread(req.userId, query_embedding, metadata_filter=where_filter, top_k=10)
        documents = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]

        # Debug: print raw documents and distances
        logger.error(f"[DEBUG] Raw documents from similarity search: {documents}")
        logger.error(f"[DEBUG] Raw distances from similarity search: {distances}")
        
        # Apply the same filtering logic as rag-context
        relevant_documents = []
        query_lower = query_text.lower().strip()
        
        for doc, dist in zip(documents, distances):
            doc_lower = doc.lower().strip()
            # Only skip if document is exactly the same as the query
            if doc_lower != query_lower:
                relevant_documents.append(doc)
        
        context = "\n---\n".join(relevant_documents) if relevant_documents else ""

        prompt = (
            f"Use the following context to answer the question.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query_text}\n"
            f"Answer:"
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=512,
        )

        ai_response_content = response.choices[0].message.content.strip()
        
        # Generate a unique response ID
        response_id = str(uuid.uuid4())
        
        # Store the AI response (temporarily disabled for debugging)
        try:
            ai_response_embedding = generate_embedding(ai_response_content)
            
            ai_response_metadata = {
                "userId": req.userId,
                "responseId": response_id,
                "userMessageId": f"query_{int(time.time())}",  # Generate a message ID for the query
                "content": ai_response_content,
                "createdAt": current_utc_timestamp(),
                "threadId": req.threadId or None,
                "type": "ai_response",
                "context": context,
                "model": "gpt-4o-mini",
                "query": query_text,
            }
            
            add_document(req.userId, response_id, ai_response_embedding, ai_response_metadata)
            logger.info(f"Stored AI response: {response_id}")
            
        except Exception as e:
            logger.warning(f"Failed to store AI response: {e}")
            # Continue even if storage fails

        return {
            "answer": ai_response_content,
            "context": context,
            "responseId": response_id
        }

    except OpenAIError as oe:
        logger.error(f"OpenAI API error: {oe}")
        raise HTTPException(status_code=502, detail="OpenAI API error")
    except Exception as e:
        logger.exception(f"Error in rag-generate: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate answer")


@app.post("/query", response_model=QueryResponse)
async def query_similar_messages(req: QueryRequest) -> QueryResponse:
    try:
        logger.info(f"Query request: userId={req.userId}, filters={req.filters}, query={req.query}")
        query_text = req.query[0] if isinstance(req.query, list) else req.query

        if not isinstance(query_text, str):
            raise HTTPException(status_code=400, detail="Invalid query type")

        where_filter = {}

        if req.threadId:
            where_filter["threadId"] = req.threadId

        if req.filters:
            where_filter.update(req.filters)

        query_embedding = generate_embedding(query_text)

        results = query_similar_any_thread(req.userId, query_embedding, metadata_filter=where_filter, top_k=5)

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        matches = [
            QueryMatch(content=doc, score=1 - dist, metadata=meta)
            for doc, meta, dist in zip(documents, metadatas, distances)
        ]

        return QueryResponse(matches=matches)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unhandled error in query endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to query messages")


@app.post("/query-ai-responses", response_model=QueryResponse)
async def query_ai_responses(req: QueryRequest) -> QueryResponse:
    """
    Query specifically for AI responses in the user's history
    """
    try:
        logger.info(f"Query AI responses: userId={req.userId}, filters={req.filters}, query={req.query}")
        query_text = req.query[0] if isinstance(req.query, list) else req.query

        if not isinstance(query_text, str):
            raise HTTPException(status_code=400, detail="Invalid query type")

        where_filter = {"type": "ai_response"}  # Only search AI responses

        if req.threadId:
            where_filter["threadId"] = req.threadId

        if req.filters:
            where_filter.update(req.filters)

        query_embedding = generate_embedding(query_text)

        results = query_similar_any_thread(req.userId, query_embedding, metadata_filter=where_filter, top_k=5)

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        matches = [
            QueryMatch(content=doc, score=1 - dist, metadata=meta)
            for doc, meta, dist in zip(documents, metadatas, distances)
        ]

        return QueryResponse(matches=matches)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unhandled error in query AI responses endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to query AI responses")


@app.post("/query-user-messages", response_model=QueryResponse)
async def query_user_messages(req: QueryRequest) -> QueryResponse:
    """
    Query specifically for user messages (excluding AI responses)
    """
    try:
        logger.info(f"Query user messages: userId={req.userId}, filters={req.filters}, query={req.query}")
        query_text = req.query[0] if isinstance(req.query, list) else req.query

        if not isinstance(query_text, str):
            raise HTTPException(status_code=400, detail="Invalid query type")

        # For ChromaDB, we'll query for user_message type specifically
        where_filter = {"type": "user_message"}

        if req.threadId:
            where_filter["threadId"] = req.threadId

        if req.filters:
            where_filter.update(req.filters)

        query_embedding = generate_embedding(query_text)

        results = query_similar_any_thread(req.userId, query_embedding, metadata_filter=where_filter, top_k=5)

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        matches = [
            QueryMatch(content=doc, score=1 - dist, metadata=meta)
            for doc, meta, dist in zip(documents, metadatas, distances)
        ]

        return QueryResponse(matches=matches)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unhandled error in query user messages endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to query user messages")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/debug-docs/{user_id}")
async def debug_docs(user_id: str):
    try:
        collection = get_or_create_collection(user_id)
        results = collection.query(query_embeddings=None, n_results=10)
        return results
    except Exception as e:
        logger.error(f"Error fetching debug docs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch debug documents")


@app.get("/monitoring/stats")
async def get_monitoring_stats(endpoint: str = None, user_id: str = None, limit: int = 100):
    """
    Get API call statistics from MongoDB
    """
    try:
        stats = get_api_stats(endpoint=endpoint, user_id=user_id, limit=limit)
        return {"stats": stats, "count": len(stats)}
    except Exception as e:
        logger.error(f"Error fetching monitoring stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch monitoring stats")


@app.get("/monitoring/latency")
async def get_latency_stats(endpoint: str = None, user_id: str = None):
    """
    Get average latency statistics from MongoDB
    """
    try:
        latency_stats = get_average_latency(endpoint=endpoint, user_id=user_id)
        return {"latency_stats": latency_stats}
    except Exception as e:
        logger.error(f"Error fetching latency stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch latency stats")


@app.get("/monitoring/endpoints")
async def get_endpoint_summary():
    """
    Get summary of all endpoints and their performance
    """
    try:
        # Get all unique endpoints
        endpoints = latency_collection.distinct("endpoint")
        summary = {}
        
        for endpoint in endpoints:
            stats = get_average_latency(endpoint=endpoint)
            if stats:
                summary[endpoint] = {
                    "avgLatency": round(stats["avgLatency"], 2),
                    "count": stats["count"],
                    "minLatency": stats["minLatency"],
                    "maxLatency": stats["maxLatency"]
                }
        
        return {"endpoint_summary": summary}
    except Exception as e:
        logger.error(f"Error fetching endpoint summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch endpoint summary")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT"))
    logger.info(f"Starting FastAPI server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
