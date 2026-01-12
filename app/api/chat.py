from fastapi import APIRouter, Depends, HTTPException
from app.models.chat import ChatQuery, ChatResponse
from app.services.rag_service import RAGService
from app.services.digital_twin_service import DigitalTwinService
from app.dependencies import get_rag_service, get_digital_twin_service


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/query", response_model=ChatResponse)
async def chat_query(
    query: ChatQuery,
    rag_service: RAGService = Depends(get_rag_service),
    digital_twin_service: DigitalTwinService = Depends(get_digital_twin_service)
):
    """
    Process a chat query using RAG
    
    The query can optionally include user vitals for personalized responses.
    """
    try:
        # Check if query is health-related and user wants personalized response
        additional_context = ""
        
        # If query mentions "my" or "I", try to get user vitals
        if any(word in query.query.lower() for word in ['my', 'i have', 'am i']):
            # For demo, use "demo_patient" - in production, get from auth
            vitals = digital_twin_service.get_latest_vitals("demo_patient")
            if vitals:
                additional_context = f"""
Patient's Current Vitals:
- Heart Rate: {vitals.heart_rate} bpm
- Blood Pressure: {vitals.blood_pressure_systolic}/{vitals.blood_pressure_diastolic} mmHg
- Blood Glucose: {vitals.blood_glucose} mg/dL
- Oxygen Saturation: {vitals.oxygen_saturation}%
"""
        
        # Process query with RAG
        response = rag_service.query(
            query=query.query,
            use_cache=query.use_cache,
            additional_context=additional_context
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "chat"}