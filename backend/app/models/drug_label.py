from sqlalchemy import Column, Integer, String, Text
from backend.app.core.database import Base

class DBDrugLabel(Base):
    __tablename__ = "drug_labels"

    id = Column(Integer, primary_key=True, index=True)
    drug_name = Column(String(50), nullable=False)
    section_name = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
