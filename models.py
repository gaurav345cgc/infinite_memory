from pydantic import BaseModel, Field
from typing import Optional, Union, List, Dict, Any


class EmbedRequest(BaseModel):
    userId: str = Field(..., description="User identifier")
    threadId: Optional[str] = Field(None, description="Thread or conversation ID")
    messageId: str = Field(..., description="Unique message ID")
    content: str = Field(..., description="Message text content")
    metadata: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional metadata like project, topic, stage, etc."
    )


class AIResponseRequest(BaseModel):
    userId: str = Field(..., description="User identifier")
    threadId: Optional[str] = Field(None, description="Thread or conversation ID")
    responseId: str = Field(..., description="Unique response ID")
    userMessageId: str = Field(..., description="ID of the user message this responds to")
    content: str = Field(..., description="AI response text content")
    context: Optional[str] = Field(None, description="Context used to generate this response")
    metadata: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional metadata like model used, confidence, etc."
    )


class QueryRequest(BaseModel):
    userId: str = Field(..., description="User identifier")
    threadId: Optional[str] = Field(None, description="Thread or conversation ID")
    query: Union[str, List[str]] = Field(..., description="Query text or list of queries")
    filters: Optional[Dict[str, Any]] = Field(None, description="Optional metadata filters for querying")

class EmbedResponse(BaseModel):
    status: str = "success"


class AIResponseResponse(BaseModel):
    status: str = "success"


class QueryMatch(BaseModel):
    content: str
    score: float
    metadata: Dict[str, str]  # Be explicit with key/value types


class QueryResponse(BaseModel):
    status: str = "success"
    matches: List[QueryMatch]
