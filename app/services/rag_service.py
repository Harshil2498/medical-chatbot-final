from typing import List, Optional
from app.services.embedding_service import EmbeddingService
from app.services.vector_db_service import VectorDBService
from app.services.llm_service import OllamaLLMService
from app.services.cache_service import CacheService
from app.models.chat import ChatResponse, Source, Message
from app.utils.prompt_templates import PromptTemplates
from uuid import uuid4
import time


class RAGService:
    """Retrieval Augmented Generation service with caching"""
    
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_db_service: VectorDBService,
        llm_service: OllamaLLMService,
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
        print("✅ RAG Service initialized!")
    
    def query(
        self,
        query: str,
        conversation_history: Optional[List[Message]] = None,
        use_cache: bool = True,
        additional_context: str = ""
    ) -> ChatResponse:
        """Process a RAG query with caching"""
        start_time = time.time()
        
        print(f"\n{'='*60}")
        print(f"📝 Processing query: {query[:100]}...")
        print(f"{'='*60}")
        
        # Check cache first
        if use_cache and self.cache:
            cache_key = CacheService.generate_cache_key(query)
            cached_response = self.cache.get(cache_key)
            
            if cached_response:
                print("🎯 CACHE HIT! Returning cached response")
                cached_response['cached'] = True
                cached_response['processing_time'] = time.time() - start_time
                return ChatResponse(**cached_response)
            else:
                print("❌ Cache miss - processing normally")
        
        # Step 1: Generate query embedding
        print("1️⃣  Generating query embedding...")
        query_embedding = self.embedding_service.embed_text(query)
        
        # Step 2: Retrieve relevant documents
        print("2️⃣  Searching vector database...")
        retrieved_docs = self.vector_db.similarity_search(
            query_embedding=query_embedding.tolist(),
            k=self.top_k
        )
        
        # Filter by score threshold
        filtered_docs = [
            doc for doc in retrieved_docs 
            if (1 - doc['distance']) >= self.score_threshold
        ]
        
        print(f"   📊 Found {len(filtered_docs)} relevant documents")
        
        if not filtered_docs:
            return ChatResponse(
                query=query,
                response="I don't have enough information to answer that question. Please try rephrasing or ask about a different topic.",
                sources=[],
                confidence=0.0,
                processing_time=time.time() - start_time
            )
        
        # Step 3: Build prompt
        print("3️⃣  Building prompt with context...")
        prompt = PromptTemplates.build_rag_prompt(
            query=query,
            context_documents=filtered_docs,
            conversation_history=conversation_history,
            additional_context=additional_context
        )
        
        # Step 4: Generate response
        print("4️⃣  Generating LLM response...")
        llm_response = self.llm.generate(prompt, max_tokens=500)
        
        # Step 5: Format sources
        print("5️⃣  Formatting response and sources...")
        sources = []
        for doc in filtered_docs:
            sources.append(Source(
                chunk_id=doc['id'],
                title=doc['metadata'].get('title', 'Unknown'),
                url=doc['metadata'].get('source_url', ''),
                relevance_score=1 - doc['distance'],
                excerpt=doc['document'][:200] + "..."
            ))
        
        # Calculate confidence
        confidence = sum(1 - doc['distance'] for doc in filtered_docs) / len(filtered_docs)
        
        processing_time = time.time() - start_time
        
        # Create response
        response = ChatResponse(
            query=query,
            response=llm_response,
            sources=sources,
            confidence=confidence,
            processing_time=processing_time,
            cached=False
        )
        
        # Store in cache
        if use_cache and self.cache:
            print("💾 Storing response in cache...")
            cache_key = CacheService.generate_cache_key(query)
            cache_data = response.dict(exclude={'cached', 'processing_time'})
            self.cache.set(cache_key, cache_data, ttl=3600)
        
        print(f"✅ Response generated in {processing_time:.2f}s")
        print(f"   Confidence: {confidence:.2f}")
        print(f"{'='*60}\n")
        
        return response