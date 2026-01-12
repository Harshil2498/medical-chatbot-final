# app/models/chat.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4


class Message(BaseModel):
    """Represents a single message in a conversation"""
    id: UUID = Field(default_factory=uuid4)
    role: str = Field(..., description="user, assistant, or system")
    content: str = Field(..., min_length=1, max_length=10000)
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['user', 'assistant', 'system']:
            raise ValueError('Role must be user, assistant, or system')
        return v


class ChatQuery(BaseModel):
    """Request model for chat queries"""
    query: str = Field(..., min_length=1, max_length=1000)
    conversation_id: Optional[UUID] = None
    use_cache: bool = True
    
    @validator('query')
    def sanitize_query(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Query cannot be empty after stripping')
        return v


class Source(BaseModel):
    """Represents a source document"""
    chunk_id: str
    title: str
    url: str
    relevance_score: float
    excerpt: str = Field(..., max_length=500)


class ChatResponse(BaseModel):
    """Response model for chat queries"""
    query: str
    response: str
    sources: List[Source]
    conversation_id: UUID = Field(default_factory=uuid4)
    confidence: float = Field(..., ge=0.0, le=1.0)
    cached: bool = False
    processing_time: float = 0.0
    metadata: Dict[str, Any] = {}