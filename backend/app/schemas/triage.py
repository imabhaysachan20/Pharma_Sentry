import datetime
from typing import Optional
from pydantic import BaseModel, Field

class IntakeRequest(BaseModel):
    narrative: str

class CaseResponse(BaseModel):
    id: int
    narrative: str
    redacted_narrative: str
    patient_name: Optional[str]
    patient_age: Optional[int]
    patient_gender: Optional[str]
    suspect_drug: str
    adverse_event: str
    seriousness: str
    signal_caveat: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Schema used for Structured Output from Strands Agent
class TriageCaseExtraction(BaseModel):
    patient_name: Optional[str] = Field(None, description="Patient name if present, otherwise null.")
    patient_age: Optional[int] = Field(None, description="Patient age in years if present, otherwise null.")
    patient_gender: Optional[str] = Field(None, description="Patient gender (e.g. Male, Female) if present, otherwise null.")
    suspect_drug: str = Field(description="The primary drug suspect in the adverse event (e.g. Aspirin, Metformin, Lisinopril).")
    adverse_event: str = Field(description="Brief summary of the adverse events reported (e.g. hives, lactic acidosis, cough).")
    seriousness: str = Field(description="Return 'Serious' or 'Non-Serious'. Serious if it indicates death, hospitalization, disability, life-threatening, or other medically significant event.")
