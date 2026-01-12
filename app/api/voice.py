from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse
from app.services.voice_service import VoiceService
from app.services.rag_service import RAGService
from app.dependencies import get_voice_service, get_rag_service
from pydantic import BaseModel
import tempfile
import os


router = APIRouter(prefix="/voice", tags=["voice"])


class TTSRequest(BaseModel):
    """Request for text-to-speech"""
    text: str


@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    voice_service: VoiceService = Depends(get_voice_service)
):
    """Convert speech to text"""
    temp_file = tempfile.NamedTemporaryFile(
        delete=False, 
        suffix=os.path.splitext(audio.filename)[1]
    )
    
    try:
        content = await audio.read()
        temp_file.write(content)
        temp_file.close()
        
        transcription = voice_service.transcribe_audio(temp_file.name)
        os.unlink(temp_file.name)
        
        return {
            "transcription": transcription,
            "filename": audio.filename
        }
    
    except Exception as e:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/synthesize")
async def synthesize_speech(
    request: TTSRequest,
    voice_service: VoiceService = Depends(get_voice_service)
):
    """Convert text to speech - returns audio file"""
    try:
        audio_path = voice_service.synthesize_speech(request.text)
        
        return FileResponse(
            path=audio_path,
            media_type="audio/mpeg",
            filename="response.mp3"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def voice_chat(
    audio: UploadFile = File(...),
    voice_service: VoiceService = Depends(get_voice_service),
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Complete voice interaction: audio in → answer → audio out
    """
    temp_input = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    
    try:
        content = await audio.read()
        temp_input.write(content)
        temp_input.close()
        
        # Transcribe
        question = voice_service.transcribe_audio(temp_input.name)
        
        # Get answer
        response = rag_service.query(question)
        
        # Convert to speech
        audio_path = voice_service.synthesize_speech(response.response)
        
        os.unlink(temp_input.name)
        
        return FileResponse(
            path=audio_path,
            media_type="audio/mpeg",
            filename="answer.mp3",
            headers={
                "X-Transcription": question,
                "X-Confidence": str(response.confidence)
            }
        )
    
    except Exception as e:
        if os.path.exists(temp_input.name):
            os.unlink(temp_input.name)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "service": "voice"}