from fastapi import APIRouter, Depends
from app.services.cache_service import CacheService
from app.services.vector_db_service import VectorDBService
from app.dependencies import get_cache_service, get_vector_db_service


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
async def get_stats(
    cache_service: CacheService = Depends(get_cache_service),
    vector_db: VectorDBService = Depends(get_vector_db_service)
):
    """Get system statistics"""
    cache_stats = cache_service.get_stats()
    
    return {
        "vector_db": {
            "total_documents": vector_db.get_collection_count(),
            "collection_name": vector_db.collection_name
        },
        "cache": cache_stats,
        "status": "healthy"
    }


@router.post("/cache/clear")
async def clear_cache(
    cache_service: CacheService = Depends(get_cache_service)
):
    """Clear all cache (use carefully!)"""
    cache_service.clear_all()
    return {"message": "Cache cleared successfully"}


@router.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "service": "admin"}