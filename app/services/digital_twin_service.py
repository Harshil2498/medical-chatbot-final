from typing import List, Optional
from datetime import datetime, timedelta
from app.models.vitals import VitalSigns, VitalsCreate
import random


class DigitalTwinService:
    """Manages patient vitals and health data"""
    
    def __init__(self):
        # In-memory storage for demo (in production, use database)
        self.vitals_storage: dict[str, List[VitalSigns]] = {}
        print("✅ Digital Twin Service initialized!")
    
    def create_vitals(self, vitals_data: VitalsCreate) -> VitalSigns:
        """Create new vital signs record"""
        vitals = VitalSigns(
            user_id=vitals_data.user_id,
            heart_rate=vitals_data.heart_rate,
            blood_pressure_systolic=vitals_data.blood_pressure_systolic,
            blood_pressure_diastolic=vitals_data.blood_pressure_diastolic,
            blood_glucose=vitals_data.blood_glucose,
            temperature=vitals_data.temperature,
            oxygen_saturation=vitals_data.oxygen_saturation,
            weight=vitals_data.weight
        )
        
        if vitals.user_id not in self.vitals_storage:
            self.vitals_storage[vitals.user_id] = []
        
        self.vitals_storage[vitals.user_id].append(vitals)
        
        print(f"✅ Created vitals for user: {vitals.user_id}")
        return vitals
    
    def get_latest_vitals(self, user_id: str) -> Optional[VitalSigns]:
        """Get most recent vitals for a user"""
        if user_id not in self.vitals_storage or not self.vitals_storage[user_id]:
            return None
        
        return self.vitals_storage[user_id][-1]
    
    def get_vitals_history(
        self, 
        user_id: str, 
        days: int = 30
    ) -> List[VitalSigns]:
        """Get vitals history for specified days"""
        if user_id not in self.vitals_storage:
            return []
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return [
            v for v in self.vitals_storage[user_id]
            if v.recorded_at >= cutoff_date
        ]
    
    def generate_mock_data(self, user_id: str, days: int = 30) -> List[VitalSigns]:
        """Generate mock vitals data for testing"""
        print(f"📊 Generating {days} days of mock data for {user_id}...")
        
        vitals_list = []
        base_date = datetime.utcnow()
        
        for i in range(days):
            recorded_at = base_date - timedelta(days=days-i)
            
            vitals = VitalSigns(
                user_id=user_id,
                recorded_at=recorded_at,
                heart_rate=random.randint(65, 85) + random.randint(-5, 5),
                blood_pressure_systolic=random.randint(115, 135) + random.randint(-5, 5),
                blood_pressure_diastolic=random.randint(75, 85) + random.randint(-3, 3),
                blood_glucose=round(random.uniform(85, 115) + random.uniform(-5, 5), 1),
                temperature=round(98.6 + random.uniform(-0.3, 0.3), 1),
                oxygen_saturation=random.randint(96, 100)
            )
            
            vitals_list.append(vitals)
        
        self.vitals_storage[user_id] = vitals_list
        print(f"✅ Generated {len(vitals_list)} mock vitals records")
        
        return vitals_list
    
    def get_vitals_summary(self, user_id: str) -> dict:
        """Get summary statistics of vitals"""
        history = self.get_vitals_history(user_id, days=30)
        
        if not history:
            return {
                "user_id": user_id,
                "message": "No data available"
            }
        
        latest = history[-1]
        
        # Calculate averages
        avg_hr = sum(v.heart_rate for v in history if v.heart_rate) / len([v for v in history if v.heart_rate])
        avg_bp_sys = sum(v.blood_pressure_systolic for v in history if v.blood_pressure_systolic) / len([v for v in history if v.blood_pressure_systolic])
        avg_glucose = sum(v.blood_glucose for v in history if v.blood_glucose) / len([v for v in history if v.blood_glucose])
        
        return {
            "user_id": user_id,
            "latest_reading": latest.dict(),
            "30_day_averages": {
                "heart_rate": round(avg_hr, 1),
                "blood_pressure_systolic": round(avg_bp_sys, 1),
                "blood_glucose": round(avg_glucose, 1)
            },
            "total_readings": len(history),
            "alerts": latest.get_alerts()
        }
