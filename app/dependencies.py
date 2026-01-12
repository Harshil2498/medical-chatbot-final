from functools import lru_cache
from app.config import get_settings
from app.services.embedding_service import EmbeddingService
from app.services.vector_db_service import VectorDBService
from app.services.llm_service import OllamaLLMService
from app.services.rag_service import RAGService
from app.services.cache_service import CacheService
from app.services.voice_service import VoiceService
from app.services.digital_twin_service import DigitalTwinService


# Global service instances (singletons)
_embedding_service = None
_vector_db_service = None
_llm_service = None
_rag_service = None
_cache_service = None
_voice_service = None
_digital_twin_service = None


def get_embedding_service() -> EmbeddingService:
    """Get embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        settings = get_settings()
        _embedding_service = EmbeddingService(settings.EMBEDDING_MODEL_NAME)
    return _embedding_service


def get_vector_db_service() -> VectorDBService:
    """Get vector DB service instance"""
    global _vector_db_service
    if _vector_db_service is None:
        settings = get_settings()
        _vector_db_service = VectorDBService(
            persist_dir=settings.CHROMA_PERSIST_DIR,
            collection_name=settings.CHROMA_COLLECTION_NAME
        )
    return _vector_db_service


def get_llm_service() -> OllamaLLMService:
    """Get LLM service instance"""
    global _llm_service
    if _llm_service is None:
        settings = get_settings()
        _llm_service = OllamaLLMService(
            base_url=settings.OLLAMA_BASE_URL,
            model_name=settings.LLM_MODEL_NAME
        )
    return _llm_service


def get_cache_service() -> CacheService:
    """Get cache service instance"""
    global _cache_service
    if _cache_service is None:
        settings = get_settings()
        _cache_service = CacheService(settings.REDIS_URL)
    return _cache_service


def get_rag_service() -> RAGService:
    """Get RAG service instance"""
    global _rag_service
    if _rag_service is None:
        settings = get_settings()
        _rag_service = RAGService(
            embedding_service=get_embedding_service(),
            vector_db_service=get_vector_db_service(),
            llm_service=get_llm_service(),
            cache_service=get_cache_service(),
            top_k=settings.RAG_TOP_K,
            score_threshold=settings.RAG_SCORE_THRESHOLD
        )
    return _rag_service


def get_voice_service() -> VoiceService:
    """Get voice service instance"""
    global _voice_service
    if _voice_service is None:
        settings = get_settings()
        _voice_service = VoiceService(
            whisper_model_size=settings.WHISPER_MODEL_SIZE
        )
    return _voice_service


def get_digital_twin_service() -> DigitalTwinService:
    """Get digital twin service instance"""
    global _digital_twin_service
    if _digital_twin_service is None:
        _digital_twin_service = DigitalTwinService()
    return _digital_twin_service