import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from backend.app.core.database import Base

class DBTriageCase(Base):
    __tablename__ = "triage_cases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    narrative = Column(Text, nullable=False)
    redacted_narrative = Column(Text, nullable=False)
    patient_name = Column(String(255))
    patient_age = Column(Integer)
    patient_gender = Column(String(50))
    suspect_drug = Column(String(100), nullable=False)
    adverse_event = Column(Text, nullable=False)
    seriousness = Column(String(50), nullable=False)
    signal_caveat = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
