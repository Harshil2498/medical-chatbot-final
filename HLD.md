# Medical Chatbot MVP - High Level Design (HLD)

## 1. System Overview

### 1.1 Purpose
A medical information retrieval chatbot that uses RAG to provide accurate, source-backed answers to health-related queries with voice interaction and health metrics visualization.

### 1.2 Key Components
1. **Data Ingestion Pipeline**: Scrapes and processes medical content
2. **Knowledge Base**: Vector store of embedded medical documents
3. **RAG Engine**: Retrieval and generation pipeline
4. **LLM Service**: Local Llama/Mistral model via Ollama
5. **Caching Layer**: Redis for query and embedding cache
6. **Conversation Manager**: Context and session management
7. **Voice Interface**: STT/TTS services
8. **Digital Twin Service**: Health metrics visualization
9. **API Gateway**: FastAPI web service
10. **Frontend**: Web UI for interaction

## 2. Architecture Patterns

### 2.1 Architectural Style
**Microservices-inspired Modular Monolith**

**Rationale**:
- MVP doesn't need full microservices complexity
- Modular design allows future service extraction
- Single deployment simplifies demo
- Clear separation of concerns

### 2.2 Key Patterns Applied

#### Pattern 1: RAG (Retrieval Augmented Generation)
```
Query → Embed → Vector Search → Retrieve Context → LLM Generate → Response
```
**Why**: Reduces hallucinations, provides source attribution

#### Pattern 2: Chain of Responsibility (CoR)
```
Request → Cache Check → Vector Retrieval → LLM → Post-processing → Response
```
**Why**: Modular processing, easy to add/remove steps

#### Pattern 3: Repository Pattern
```
Service Layer → Repository Interface → Concrete Repositories (Vector DB, SQL DB)
```
**Why**: Abstracts data access, easy to swap implementations

#### Pattern 4: Cache-Aside
```
Query → Check Cache → [Hit: Return] / [Miss: Compute → Store → Return]
```
**Why**: Performance optimization, reduced LLM calls

#### Pattern 5: Adapter Pattern
```
LLM Service Interface → Ollama Adapter | OpenAI Adapter | HuggingFace Adapter
```
**Why**: Easy to swap LLM providers

## 3. Component Design

### 3.1 Data Ingestion Pipeline

```
Web Scraper → Document Parser → Text Chunker → Embedder → Vector Store
```

**Responsibilities**:
- Scrape medical websites (BeautifulSoup4/Scrapy)
- Extract clean text (trafilatura)
- Chunk documents (LangChain TextSplitter)
- Generate embeddings (sentence-transformers)
- Store in ChromaDB with metadata

**Key Decisions**:
- **Chunk Size**: 512 tokens with 50-token overlap
  - Why: Balance between context and retrieval granularity
- **Metadata**: source_url, title, date, category, chunk_id
  - Why: Enables filtering and source attribution

**Data Flow**:
```python
# Pseudo-code
urls = load_medical_urls()
for url in urls:
    html = scrape(url)
    text = extract_text(html)
    chunks = split_into_chunks(text, size=512, overlap=50)
    for chunk in chunks:
        embedding = embed_model.encode(chunk)
        vector_db.add(
            embedding=embedding,
            text=chunk,
            metadata={'source': url, 'title': extract_title(html)}
        )
```

### 3.2 Vector Database Service

**Technology**: ChromaDB (primary), FAISS (alternative)

**Schema**:
```python
Collection: "medical_knowledge"
{
    "id": "chunk_uuid",
    "embedding": [768-dim vector],
    "document": "chunk text",
    "metadata": {
        "source_url": "https://...",
        "title": "Article Title",
        "category": "diabetes|hypertension|...",
        "date_scraped": "2024-01-15",
        "chunk_index": 0
    }
}
```

**Operations**:
- `add_documents(texts, metadatas)`: Bulk insert
- `similarity_search(query, k=5, filter={})`: Retrieve relevant chunks
- `get_by_id(chunk_id)`: Fetch specific chunk

**Optimizations**:
- Index type: HNSW (Hierarchical Navigable Small World) for fast ANN search
- Distance metric: Cosine similarity
- Pre-filtering by metadata before vector search

### 3.3 RAG Engine

**Core Algorithm**:
```python
def rag_query(user_query: str, conversation_history: List[Message]) -> Response:
    # Step 1: Contextualize query with history
    contextualized_query = rewrite_query(user_query, conversation_history)
    
    # Step 2: Generate embedding
    query_embedding = embedding_model.encode(contextualized_query)
    
    # Step 3: Retrieve relevant chunks
    relevant_docs = vector_db.similarity_search(
        query_embedding, 
        k=5, 
        score_threshold=0.7
    )
    
    # Step 4: Construct prompt
    context = "\n\n".join([doc.text for doc in relevant_docs])
    prompt = build_prompt(
        system="You are a medical information assistant...",
        context=context,
        query=user_query,
        history=conversation_history[-5:]  # Last 5 turns
    )
    
    # Step 5: LLM generation
    response = llm.generate(prompt, max_tokens=500)
    
    # Step 6: Post-process and add sources
    return Response(
        text=response,
        sources=[doc.metadata for doc in relevant_docs],
        confidence=calculate_confidence(relevant_docs)
    )
```

**Chain-of-Thought Enhancement**:
```python
# For complex queries, use multi-step reasoning
cot_prompt = """
Let's approach this step-by-step:
1. First, identify the key medical concepts in the question
2. Then, retrieve relevant information from the context
3. Finally, synthesize a comprehensive answer

Context: {context}
Question: {query}

Step 1 - Key Concepts:
"""
```

### 3.4 LLM Service

**Interface**:
```python
class LLMService(ABC):
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int, temperature: float) -> str:
        pass
    
    @abstractmethod
    def stream_generate(self, prompt: str) -> Iterator[str]:
        pass
```

**Ollama Implementation**:
```python
class OllamaLLM(LLMService):
    def __init__(self, model_name="llama3.1:8b"):
        self.model = model_name
        self.client = ollama.Client()
    
    def generate(self, prompt, max_tokens=500, temperature=0.7):
        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            options={
                'num_predict': max_tokens,
                'temperature': temperature
            }
        )
        return response['response']
```

**Configuration**:
- Model: llama3.1:8b or mistral:7b
- Temperature: 0.7 (balance creativity and consistency)
- Top-p: 0.9
- Context window: 4096 tokens
- Stop sequences: ["\n\nHuman:", "Sources:"]

### 3.5 Caching Layer

**Two-Level Cache**:

#### L1: Query Cache (Redis)
```python
# Cache structure
key: "query:{hash(user_query)}"
value: {
    "response": "...",
    "sources": [...],
    "timestamp": "2024-01-15T10:30:00Z"
}
ttl: 3600 seconds (1 hour)
```

#### L2: Embedding Cache (Disk/Redis)
```python
key: "embedding:{hash(text)}"
value: [768-dim vector bytes]
ttl: 86400 seconds (24 hours)
```

**Cache Strategy**:
```python
def get_cached_response(query: str) -> Optional[Response]:
    cache_key = f"query:{hash_query(query)}"
    cached = redis_client.get(cache_key)
    if cached:
        logger.info(f"Cache hit for query: {query[:50]}")
        return Response.parse(cached)
    return None

def set_cache(query: str, response: Response):
    cache_key = f"query:{hash_query(query)}"
    redis_client.setex(
        cache_key, 
        3600,  # 1 hour TTL
        response.json()
    )
```

**Cache Invalidation**:
- Time-based: TTL of 1 hour for queries
- Event-based: Clear on knowledge base update

### 3.6 Conversation Manager

**Session Storage** (PostgreSQL/SQLite):
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    role VARCHAR(10),  -- 'user' or 'assistant'
    content TEXT,
    metadata JSONB,  -- sources, confidence, etc.
    timestamp TIMESTAMP
);
```

**Context Window Management**:
```python
class ConversationManager:
    def __init__(self, max_history=5):
        self.max_history = max_history
    
    def get_context(self, conversation_id: UUID) -> List[Message]:
        # Retrieve last N messages
        messages = db.query(Message)\
            .filter(Message.conversation_id == conversation_id)\
            .order_by(Message.timestamp.desc())\
            .limit(self.max_history * 2)  # user + assistant
        return list(reversed(messages))
    
    def add_message(self, conversation_id: UUID, role: str, content: str):
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            timestamp=datetime.utcnow()
        )
        db.add(message)
        db.commit()
```

### 3.7 Voice Interface

**STT Service (Whisper)**:
```python
class SpeechToTextService:
    def __init__(self, model_size="base"):
        self.model = whisper.load_model(model_size)
    
    def transcribe(self, audio_file_path: str) -> str:
        result = self.model.transcribe(audio_file_path)
        return result["text"]
```

**TTS Service (pyttsx3)**:
```python
class TextToSpeechService:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speed
        self.engine.setProperty('volume', 0.9)
    
    def synthesize(self, text: str, output_path: str):
        self.engine.save_to_file(text, output_path)
        self.engine.runAndWait()
```

**Audio Pipeline**:
```
Browser → WebRTC/File Upload → STT → Text Query → RAG → TTS → Audio Response
```

### 3.8 Digital Twin Service

**MVP Approach: 2D Health Dashboard**

**Data Model**:
```python
@dataclass
class PatientVitals:
    user_id: str
    timestamp: datetime
    heart_rate: int  # bpm
    blood_pressure: Tuple[int, int]  # systolic, diastolic
    blood_glucose: float  # mg/dL
    temperature: float  # °F
    oxygen_saturation: int  # %
```

**Visualization Components**:
1. **Time-series Charts**: Heart rate, BP over time (Plotly)
2. **Gauge Charts**: Current vitals vs. normal ranges
3. **Alert System**: Highlight abnormal values
4. **Trend Analysis**: Show improving/worsening trends

**Integration with Chatbot**:
```python
# When user asks "What's my current blood pressure?"
vitals = digital_twin_service.get_latest_vitals(user_id)
context_addition = f"Patient's current BP: {vitals.blood_pressure}"
# Include in RAG context for personalized response
```

**Mock Data for Demo**:
```python
# Generate realistic synthetic data
def generate_mock_vitals(days=30):
    return [
        PatientVitals(
            user_id="demo_patient",
            timestamp=datetime.now() - timedelta(days=i),
            heart_rate=random.randint(60, 100),
            blood_pressure=(random.randint(110, 140), random.randint(70, 90)),
            blood_glucose=random.uniform(70, 130),
            # ...
        )
        for i in range(days)
    ]
```

### 3.9 API Gateway (FastAPI)

**Endpoints**:

```python
# Health check
GET /health

# Chat endpoints
POST /chat/query
{
    "query": "What are symptoms of diabetes?",
    "conversation_id": "uuid-optional",
    "use_voice": false
}

# Voice endpoints
POST /voice/transcribe
Content-Type: multipart/form-data
{
    "audio": 
}

POST /voice/synthesize
{
    "text": "Response to speak"
}

# Digital twin endpoints
GET /digital-twin/vitals/{user_id}
POST /digital-twin/vitals
{
    "user_id": "...",
    "vitals": {...}
}

# Knowledge base management
POST /admin/ingest
{
    "url": "https://medical-site.com/article"
}

GET /admin/stats
# Returns KB size, cache hit rate, etc.
```

**WebSocket for Streaming**:
```python
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    while True:
        query = await websocket.receive_text()
        async for chunk in rag_engine.stream_query(query):
            await websocket.send_text(chunk)
```

## 4. Data Flow Diagrams

### 4.1 Query Processing Flow

```
[User Input] 
    ↓
[API Gateway] 
    ↓
[Cache Check] → [Cache Hit] → [Return Response]
    ↓ (Miss)
[Conversation Manager] ← Get History
    ↓
[Query Rewriter] ← Contextualize with history
    ↓
[Embedding Service] → [Check Embedding Cache]
    ↓
[Vector DB] ← Similarity Search
    ↓
[RAG Engine] ← Retrieve top-k docs
    ↓
[Prompt Builder] ← Construct prompt with context
    ↓
[LLM Service (Ollama)]
    ↓
[Response Post-processor] ← Add sources, format
    ↓
[Cache] ← Store result
    ↓
[Conversation Manager] ← Save message
    ↓
[API Gateway] → Return to user
```

### 4.2 Voice Interaction Flow

```
[User Voice Input]
    ↓
[Frontend] → Record Audio
    ↓
[API: /voice/transcribe]
    ↓
[STT Service (Whisper)]
    ↓
[Transcribed Text]
    ↓
[Standard Query Processing] (See 4.1)
    ↓
[Text Response]
    ↓
[API: /voice/synthesize]
    ↓
[TTS Service]
    ↓
[Audio Response]
    ↓
[Frontend] → Play Audio
```

### 4.3 Data Ingestion Flow

```
[Medical Websites]
    ↓
[Web Scraper] → BeautifulSoup4/Scrapy
    ↓
[HTML Content]
    ↓
[Text Extractor] → trafilatura
    ↓
[Clean Text]
    ↓
[Metadata Extractor] → Title, date, category
    ↓
[Text Chunker] → LangChain RecursiveCharacterTextSplitter
    ↓
[Chunks (512 tokens each)]
    ↓
[Embedding Generator] → sentence-transformers
    ↓
[Vector + Text + Metadata]
    ↓
[ChromaDB] → Persist to disk
    ↓
[Knowledge Base Ready]
```

## 5. Database Design

### 5.1 PostgreSQL Schema (Conversation & User Data)

```sql
-- Users (optional for MVP)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Conversations
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),  -- Auto-generated from first query
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB  -- Store settings, preferences
);

-- Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(10) CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB,  -- sources, confidence, retrieval_docs, etc.
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_conversation_time (conversation_id, created_at)
);

-- Digital Twin - Patient Vitals
CREATE TABLE patient_vitals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    recorded_at TIMESTAMP NOT NULL,
    heart_rate INTEGER,
    blood_pressure_systolic INTEGER,
    blood_pressure_diastolic INTEGER,
    blood_glucose DECIMAL(5,2),
    temperature DECIMAL(4,2),
    oxygen_saturation INTEGER,
    weight DECIMAL(5,2),
    metadata JSONB,  -- Additional metrics
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_time (user_id, recorded_at)
);

-- Cache Metadata (optional, if not using Redis)
CREATE TABLE query_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_hash VARCHAR(64) UNIQUE,
    query_text TEXT,
    response JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    hit_count INTEGER DEFAULT 0,
    INDEX idx_query_hash (query_hash),
    INDEX idx_expires (expires_at)
);
```

### 5.2 Vector Database (ChromaDB)

**Collection Structure**:
```python
{
    "name": "medical_knowledge",
    "metadata": {
        "description": "Embedded medical articles and documents",
        "embedding_model": "all-MiniLM-L6-v2",
        "chunk_size": 512,
        "chunk_overlap": 50
    },
    "embedding_dimension": 384
}
```

**Document Schema**:
```python
{
    "id": "doc_uuid",
    "embedding": [384-dimensional float vector],
    "document": "Actual text chunk",
    "metadata": {
        "source_url": "https://...",
        "source_title": "Understanding Diabetes",
        "category": "endocrinology",
        "date_published": "2023-05-10",
        "date_scraped": "2024-01-15",
        "chunk_index": 0,
        "total_chunks": 15,
        "keywords": ["diabetes", "insulin", "glucose"]
    }
}
```

**Indexing Strategy**:
- Use HNSW index for fast approximate nearest neighbor search
- M parameter: 16 (connections per node)
- ef_construction: 200 (search depth during construction)

## 6. Security Considerations

### 6.1 Authentication & Authorization
- **MVP**: Simple API key for admin endpoints
- **Production**: OAuth2 + JWT tokens

### 6.2 Input Validation
```python
from pydantic import BaseModel, validator

class ChatQuery(BaseModel):
    query: str
    conversation_id: Optional[UUID]
    
    @validator('query')
    def query_not_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Query cannot be empty')
        if len(v) > 1000:
            raise ValueError('Query too long (max 1000 chars)')
        return v.strip()
```

### 6.3 Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/chat/query")
@limiter.limit("30/minute")  # 30 requests per minute
async def chat_query(request: Request, query: ChatQuery):
    # ...
```

### 6.4 Prompt Injection Prevention
```python
def sanitize_query(query: str) -> str:
    # Remove potential prompt injection attempts
    dangerous_patterns = [
        r"ignore previous instructions",
        r"disregard.*above",
        r"you are now",
    ]
    for pattern in dangerous_patterns:
        query = re.sub(pattern, "", query, flags=re.IGNORECASE)
    return query
```

## 7. Monitoring & Logging

### 7.1 Metrics to Track
- Request latency (p50, p95, p99)
- Cache hit rate
- Vector search duration
- LLM inference time
- Error rates by endpoint

### 7.2 Logging Strategy
```python
import structlog

logger = structlog.get_logger()

# Structured logging
logger.info(
    "query_processed",
    query=query[:50],
    retrieval_time=retrieval_duration,
    llm_time=llm_duration,
    cache_hit=cache_hit,
    num_sources=len(sources)
)
```

### 7.3 Tools
- **Logging**: structlog + file rotation
- **Metrics**: Prometheus (if time permits)
- **Tracing**: OpenTelemetry (nice-to-have)

## 8. Scalability Considerations

### 8.1 Horizontal Scaling
- Stateless API servers behind load balancer
- Shared Redis cache
- Shared PostgreSQL database
- Vector DB can be scaled to distributed setup (Milvus/Weaviate)

### 8.2 Performance Optimizations
1. **Batch Embedding**: Process multiple queries together
2. **Model Quantization**: Use 4-bit quantized LLMs (llama.cpp)
3. **Async Processing**: FastAPI + async/await throughout
4. **Connection Pooling**: DB and Redis connection pools

### 8.3 Future Enhancements
- Multi-GPU inference
- Model serving via TensorRT/vLLM
- Dedicated embedding service
- CDN for static assets

## 9. Deployment Architecture

### 9.1 MVP Deployment (Single Server)
```
[Nginx Reverse Proxy]
    ↓
[FastAPI Application]
    ├─ LLM Service (Ollama)
    ├─ Embedding Service
    └─ ChromaDB
    ↓
[PostgreSQL]
[Redis]
```

### 9.2 Docker Compose Setup
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
      - ollama
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres/medicalbot
      - REDIS_URL=redis://redis:6379
      - OLLAMA_HOST=http://ollama:11434
  
  postgres:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    
  ollama:
    image: ollama/ollama
    volumes:
      - ollama_data:/root/.ollama
```

## 10. Testing Strategy (High-Level)

### 10.1 Unit Tests
- Test individual components (embedder, chunker, cache)
- Mock external dependencies (LLM, DB)
- Coverage target: >70%

### 10.2 Integration Tests
- Test RAG pipeline end-to-end
- Test API endpoints
- Test database interactions

### 10.3 Performance Tests
- Load testing with locust
- Measure response times under load
- Cache effectiveness

### 10.4 Quality Tests
- RAG retrieval precision (manual evaluation)
- Answer relevance scoring
- Source attribution accuracy
