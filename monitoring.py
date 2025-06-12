import os
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging
from pymongo import MongoClient
from logging_config import setup_logging

# Initialize logger
logger = setup_logging(__name__)

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri)
db = client.get_database("eoxs_monitoring")
api_calls_collection = db.get_collection("api_calls")
latency_collection = db.get_collection("latency")

def log_api_call(
    endpoint: str,
    user_id: Optional[str] = None,
    message_id: Optional[str] = None,
    thread_id: Optional[str] = None,
    query: Optional[str] = None,
    duration_ms: float = 0.0,
    status: str = "success",
    error: Optional[str] = None
) -> None:
    """
    Log API call details to MongoDB for monitoring
    """
    try:
        log_entry = {
            "timestamp": datetime.utcnow(),
            "endpoint": endpoint,
            "userId": user_id,
            "messageId": message_id,
            "threadId": thread_id,
            "query": query,
            "durationMs": duration_ms,
            "status": status,
            "error": error
        }
        
        # Insert into MongoDB
        api_calls_collection.insert_one(log_entry)
        
        # Also log to latency collection for performance tracking
        latency_entry = {
            "timestamp": datetime.utcnow(),
            "endpoint": endpoint,
            "userId": user_id,
            "durationMs": duration_ms,
            "status": status
        }
        latency_collection.insert_one(latency_entry)
        
        logger.info(f"📊 API Call logged: {endpoint} | Status: {status} | Duration: {duration_ms}ms")
        
    except Exception as e:
        logger.error(f"Failed to log API call: {e}", exc_info=True)

def get_api_stats(
    endpoint: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Get API call statistics from MongoDB
    """
    try:
        filter_query = {}
        if endpoint:
            filter_query["endpoint"] = endpoint
        if user_id:
            filter_query["userId"] = user_id
            
        cursor = api_calls_collection.find(filter_query).sort("timestamp", -1).limit(limit)
        return list(cursor)
        
    except Exception as e:
        logger.error(f"Failed to get API stats: {e}", exc_info=True)
        return []

def get_average_latency(
    endpoint: Optional[str] = None,
    user_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Get average latency statistics from MongoDB
    """
    try:
        filter_query = {"status": "success"}
        if endpoint:
            filter_query["endpoint"] = endpoint
        if user_id:
            filter_query["userId"] = user_id
            
        pipeline = [
            {"$match": filter_query},
            {"$group": {
                "_id": None,
                "avgLatency": {"$avg": "$durationMs"},
                "minLatency": {"$min": "$durationMs"},
                "maxLatency": {"$max": "$durationMs"},
                "count": {"$sum": 1}
            }}
        ]
        
        result = list(latency_collection.aggregate(pipeline))
        if result:
            return result[0]
        return None
        
    except Exception as e:
        logger.error(f"Failed to get latency stats: {e}", exc_info=True)
        return None 