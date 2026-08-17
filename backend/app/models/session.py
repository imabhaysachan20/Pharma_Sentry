import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from backend.app.core.database import Base

class DBSession(Base):
    __tablename__ = "sessions"

    id = Column(String(255), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    agentcore_session_id = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
