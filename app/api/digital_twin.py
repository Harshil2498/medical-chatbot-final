from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.vitals import VitalSigns, VitalsCreate
from app.services.digital_twin_service import DigitalTwinService
from app.dependencies import get_digital_twin_service


router = APIRouter(prefix="/digital-twin", tags=["digital-twin"])


@router.post("/vitals", response_model=VitalSigns)
async def create_vitals(
    vitals_data: VitalsCreate,
    service: DigitalTwinService = Depends(get_digital_twin_service)
):
    """Create new vital signs record"""
    try:
        return service.create_vitals(vitals_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vitals/{user_id}/latest", response_model=VitalSigns)
async def get_latest_vitals(
    user_id: str,
    service: DigitalTwinService = Depends(get_digital_twin_service)
):
    """Get most recent vitals for a user"""
    vitals = service.get_latest_vitals(user_id)
    if not vitals:
        raise HTTPException(status_code=404, detail="No vitals found for user")
    return vitals


@router.get("/vitals/{user_id}/history", response_model=List[VitalSigns])
async def get_vitals_history(
    user_id: str,
    days: int = 30,
    service: DigitalTwinService = Depends(get_digital_twin_service)
):
    """Get vitals history for specified days"""
    return service.get_vitals_history(user_id, days)


@router.get("/vitals/{user_id}/summary")
async def get_vitals_summary(
    user_id: str,
    service: DigitalTwinService = Depends(get_digital_twin_service)
):
    """Get summary statistics of vitals"""
    return service.get_vitals_summary(user_id)


@router.post("/vitals/{user_id}/generate-mock")
async def generate_mock_data(
    user_id: str,
    days: int = 30,
    service: DigitalTwinService = Depends(get_digital_twin_service)
):
    """Generate mock vitals data for testing"""
    vitals_list = service.generate_mock_data(user_id, days)
    return {
        "message": f"Generated {len(vitals_list)} records",
        "user_id": user_id,
        "days": days
    }


@router.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "service": "digital-twin"}