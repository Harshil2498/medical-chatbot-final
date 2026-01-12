# Medical Chatbot MVP - Low Level Design (LLD)
# This file contains detailed class designs, interfaces, and implementation specifics

"""
Project Structure:
medical_chatbot/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── models/                 # Pydantic models
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── vitals.py
│   │   └── knowledge.py
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── rag_service.py
│   │   ├── llm_service.py
│   │   ├── embedding_service.py
│   │   ├── vector_db_service.py
│   │   ├── cache_service.py
│   │   ├── conversation_service.py
│   │   ├── voice_service.py
│   │   └── digital_twin_service.py
│   ├── repositories/           # Data access layer
│   │   ├── __init__.py
│   │   ├── conversation_repo.py
│   │   └── vitals_repo.py
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── voice.py
│   │   ├── digital_twin.py
│   │   └── admin.py
│   └── utils/                  # Utilities
│       ├── __init__.py
│       ├── text_processing.py
│       ├── prompt_templates.py
│       └── validators.py
├── data_pipeline/              # Data ingestion
│   ├── __init__.py
│   ├── scrapers.py
│   ├── text_processor.py
│   └── embedder.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── frontend/                   # Web UI (React/Vue)
├── scripts/
│   ├── setup_db.py
│   ├── ingest_data.py
│   └── run_tests.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
"""

# ============================================================================
# 1. CONFIGURATION MODULE (app/config.py)
# ============================================================================

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    """Application configuration using environment variables"""
    
    # Application
    APP_NAME: str = "Medical Chatbot MVP"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/medicalbot"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1 hour
    
    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./data/chroma_db"
    CHROMA_COLLECTION_NAME: str = "medical_knowledge"
    
    # LLM Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL_NAME: str = "llama3.1:8b"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 500
    LLM_CONTEXT_WINDOW: int = 4096
    
    # Embedding Settings
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    EMBEDDING_BATCH_SIZE: int = 32
    
    # RAG Settings
    RAG_TOP_K: int = 5
    RAG_SCORE_THRESHOLD: float = 0.7
    RAG_CHUNK_SIZE: int = 512
    RAG_CHUNK_OVERLAP: int = 50
    
    # Conversation
    MAX_CONVERSATION_HISTORY: int = 5
    
    # Voice Settings
    WHISPER_MODEL_SIZE: str = "base"  # tiny, base, small, medium, large
    TTS_ENGINE: str = "pyttsx3"  # pyttsx3 or gtts
    TTS_RATE: int = 150
    TTS_VOLUME: float = 0.9
    
    # API Settings
    API_RATE_LIMIT: str = "30/minute"
    API_CORS_ORIGINS: list = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()


# ============================================================================
# 2. PYDANTIC MODELS (app/models/)
# ============================================================================

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
    stream: bool = False
    
    @validator('query')
    def sanitize_query(cls, v):
        # Basic sanitization
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
    conversation_id: UUID
    confidence: float = Field(..., ge=0.0, le=1.0)
    cached: bool = False
    processing_time: float
    metadata: Dict[str, Any] = {}

# app/models/vitals.py
class VitalSigns(BaseModel):
    """Patient vital signs"""
    user_id: str
    recorded_at: datetime
    heart_rate: Optional[int] = Field(None, ge=30, le=220, description="bpm")
    blood_pressure_systolic: Optional[int] = Field(None, ge=70, le=200)
    blood_pressure_diastolic: Optional[int] = Field(None, ge=40, le=130)
    blood_glucose: Optional[float] = Field(None, ge=20.0, le=600.0, description="mg/dL")
    temperature: Optional[float] = Field(None, ge=95.0, le=106.0, description="°F")
    oxygen_saturation: Optional[int] = Field(None, ge=70, le=100, description="%")
    weight: Optional[float] = Field(None, ge=20.0, le=500.0, description="lbs")
    
    def is_critical(self) -> bool:
        """Check if any vitals are in critical range"""
        if self.heart_rate and (self.heart_rate < 40 or self.heart_rate > 120):
            return True
        if self.blood_pressure_systolic and self.blood_pressure_systolic > 180:
            return True
        if self.oxygen_saturation and self.oxygen_saturation < 90:
            return True
        return False

# app/models/knowledge.py
class DocumentChunk(BaseModel):
    """Represents a chunk of a document"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    text: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = {}
    
class KnowledgeDocument(BaseModel):
    """Represents a full document"""
    url: str
    title: str
    content: str
    category: str
    date_published: Optional[datetime] = None
    chunks: List[DocumentChunk] = []


# ============================================================================
# 3. SERVICES - Core Business Logic
# ============================================================================

# app/services/embedding_service.py
from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
import hashlib

class EmbeddingService:
    """Handles text embedding generation with caching"""
    
    def __init__(self, model_name: str, cache_service=None):
        self.model = SentenceTransformer(model_name)
        self.cache = cache_service
        self.dimension = self.model.get_sentence_embedding_dimension()
    
    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        # Check cache first
        if self.cache:
            cache_key = self._generate_cache_key(text)
            cached = self.cache.get(cache_key)
            if cached is not None:
                return np.array(cached)
        
        # Generate embedding
        embedding = self.model.encode(text, normalize_embeddings=True)
        
        # Cache result
        if self.cache:
            self.cache.set(cache_key, embedding.tolist(), ttl=86400)  # 24h
        
        return embedding
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Generate embeddings for multiple texts"""
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=True
        )
        return embeddings
    
    def _generate_cache_key(self, text: str) -> str:
        """Generate cache key from text"""
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        return f"embedding:{text_hash}"


# app/services/vector_db_service.py
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional

class VectorDBService:
    """Manages vector database operations using ChromaDB"""
    
    def __init__(self, persist_dir: str, collection_name: str):
        self.client = chromadb.Client(ChromaSettings(
            persist_directory=persist_dir,
            anonymized_telemetry=False
        ))
        self.collection_name = collection_name
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        """Get existing collection or create new one"""
        try:
            return self.client.get_collection(name=self.collection_name)
        except:
            return self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Medical knowledge base"}
            )
    
    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ):
        """Add documents to the collection"""
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
    
    def similarity_search(
        self,
        query_embedding: List[float],
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=filter_dict if filter_dict else None
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'id': results['ids'][0][i],
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })
        
        return formatted_results
    
    def get_collection_count(self) -> int:
        """Get total number of documents"""
        return self.collection.count()
    
    def delete_collection(self):
        """Delete the entire collection"""
        self.client.delete_collection(name=self.collection_name)


# app/services/cache_service.py
import redis
import json
import pickle
from typing import Any, Optional
import hashlib

class CacheService:
    """Redis-based caching service"""
    
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url, decode_responses=False)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return pickle.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL"""
        try:
            self.redis_client.setex(
                key,
                ttl,
                pickle.dumps(value)
            )
        except Exception as e:
            print(f"Cache set error: {e}")
    
    def delete(self, key: str):
        """Delete key from cache"""
        self.redis_client.delete(key)
    
    def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern"""
        for key in self.redis_client.scan_iter(pattern):
            self.redis_client.delete(key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        info = self.redis_client.info()
        return {
            'total_keys': self.redis_client.dbsize(),
            'memory_used': info.get('used_memory_human'),
            'hit_rate': info.get('keyspace_hits', 0) / 
                       max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0), 1)
        }


# app/services/llm_service.py
import requests
from typing import Iterator, Optional
from abc import ABC, abstractmethod

class BaseLLMService(ABC):
    """Abstract base class for LLM services"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        pass
    
    @abstractmethod
    def stream_generate(self, prompt: str, **kwargs) -> Iterator[str]:
        pass

class OllamaLLMService(BaseLLMService):
    """Ollama LLM service implementation"""
    
    def __init__(self, base_url: str, model_name: str):
        self.base_url = base_url
        self.model_name = model_name
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        stop_sequences: Optional[List[str]] = None
    ) -> str:
        """Generate completion from Ollama"""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                "stop": stop_sequences or []
            }
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        return response.json()['response']
    
    def stream_generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> Iterator[str]:
        """Stream completion from Ollama"""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": True,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }
        
        response = requests.post(url, json=payload, stream=True)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                if 'response' in chunk:
                    yield chunk['response']
    
    def check_health(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False


# app/services/rag_service.py
from typing import List, Dict, Any, Optional
import time
from app.utils.prompt_templates import PromptTemplates

class RAGService:
    """Retrieval Augmented Generation service"""
    
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_db_service: VectorDBService,
        llm_service: BaseLLMService,
        cache_service: Optional[CacheService] = None,
        top_k: int = 5,
        score_threshold: float = 0.7
    ):
        self.embedding_service = embedding_service
        self.vector_db = vector_db_service
        self.llm = llm_service
        self.cache = cache_service
        self.top_k = top_k
        self.score_threshold = score_threshold
    
    def query(
        self,
        query: str,
        conversation_history: Optional[List[Message]] = None,
        use_cache: bool = True
    ) -> ChatResponse:
        """Process a RAG query"""
        start_time = time.time()
        
        # Check cache
        if use_cache and self.cache:
            cache_key = self._generate_query_cache_key(query)
            cached_response = self.cache.get(cache_key)
            if cached_response:
                cached_response['cached'] = True
                cached_response['processing_time'] = time.time() - start_time
                return ChatResponse(**cached_response)
        
        # Step 1: Contextualize query with history
        contextualized_query = self._contextualize_query(query, conversation_history)
        
        # Step 2: Generate embedding
        query_embedding = self.embedding_service.embed_text(contextualized_query)
        
        # Step 3: Retrieve relevant documents
        retrieved_docs = self.vector_db.similarity_search(
            query_embedding=query_embedding.tolist(),
            k=self.top_k
        )
        
        # Filter by score threshold (convert distance to similarity)
        filtered_docs = [
            doc for doc in retrieved_docs 
            if (1 - doc['distance']) >= self.score_threshold
        ]
        
        # Step 4: Build prompt with context
        prompt = PromptTemplates.build_rag_prompt(
            query=query,
            context_documents=filtered_docs,
            conversation_history=conversation_history
        )
        
        # Step 5: Generate response
        llm_response = self.llm.generate(prompt)
        
        # Step 6: Format response
        sources = self._format_sources(filtered_docs)
        confidence = self._calculate_confidence(filtered_docs)
        
        response = ChatResponse(
            query=query,
            response=llm_response,
            sources=sources,
            conversation_id=uuid4(),
            confidence=confidence,
            cached=False,
            processing_time=time.time() - start_time
        )
        
        # Cache the response
        if use_cache and self.cache:
            self.cache.set(cache_key, response.dict(exclude={'cached', 'processing_time'}))
        
        return response
    
    def _contextualize_query(
        self,
        query: str,
        history: Optional[List[Message]]
    ) -> str:
        """Rewrite query with conversation context"""
        if not history or len(history) == 0:
            return query
        
        # Simple contextualization: append last user message
        last_messages = " ".join([
            msg.content for msg in history[-2:]  # Last 2 messages
            if msg.role == 'user'
        ])
        
        return f"{last_messages} {query}" if last_messages else query
    
    def _format_sources(self, docs: List[Dict]) -> List[Source]:
        """Format retrieved documents as sources"""
        sources = []
        for doc in docs:
            sources.append(Source(
                chunk_id=doc['id'],
                title=doc['metadata'].get('title', 'Unknown'),
                url=doc['metadata'].get('source_url', ''),
                relevance_score=1 - doc['distance'],  # Convert distance to similarity
                excerpt=doc['document'][:300] + "..."
            ))
        return sources
    
    def _calculate_confidence(self, docs: List[Dict]) -> float:
        """Calculate confidence score based on retrieval quality"""
        if not docs:
            return 0.0
        
        # Average similarity score
        avg_similarity = sum(1 - doc['distance'] for doc in docs) / len(docs)
        
        # Penalize if we have fewer than desired docs
        coverage_penalty = len(docs) / self.top_k
        
        return avg_similarity * coverage_penalty
    
    def _generate_query_cache_key(self, query: str) -> str:
        """Generate cache key for query"""
        return f"query:{hashlib.sha256(query.encode()).hexdigest()}"
