from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
from typing import List, Dict  # Add List here

class VitalSigns(BaseModel):
    """Patient vital signs"""
    id: UUID = Field(default_factory=uuid4)
    user_id: str
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
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
    
    def get_alerts(self) -> List[str]:
        """Get list of alerts for abnormal vitals"""
        alerts = []
        
        if self.heart_rate:
            if self.heart_rate < 60:
                alerts.append("Heart rate below normal (bradycardia)")
            elif self.heart_rate > 100:
                alerts.append("Heart rate above normal (tachycardia)")
        
        if self.blood_pressure_systolic:
            if self.blood_pressure_systolic >= 180:
                alerts.append("CRITICAL: Blood pressure severely elevated")
            elif self.blood_pressure_systolic >= 140:
                alerts.append("Blood pressure elevated (Stage 2 Hypertension)")
            elif self.blood_pressure_systolic >= 130:
                alerts.append("Blood pressure slightly elevated (Stage 1 Hypertension)")
        
        if self.blood_glucose:
            if self.blood_glucose < 70:
                alerts.append("Blood glucose LOW (hypoglycemia)")
            elif self.blood_glucose > 200:
                alerts.append("Blood glucose HIGH (hyperglycemia)")
            elif self.blood_glucose > 125:
                alerts.append("Blood glucose elevated (prediabetic range)")
        
        if self.oxygen_saturation:
            if self.oxygen_saturation < 90:
                alerts.append("CRITICAL: Oxygen saturation low")
            elif self.oxygen_saturation < 95:
                alerts.append("Oxygen saturation below normal")
        
        return alerts


class VitalsCreate(BaseModel):
    """Request to create new vital signs"""
    user_id: str
    heart_rate: Optional[int] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    blood_glucose: Optional[float] = None
    temperature: Optional[float] = None
    oxygen_saturation: Optional[int] = None
    weight: Optional[float] = None