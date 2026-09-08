import uuid
import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    farm_id = Column(String(36), ForeignKey("farms.id"), nullable=False, index=True)

    alert_type = Column(String(50), nullable=False)  # disease_risk | irrigation | general
    severity = Column(String(20), default="medium")  # low | medium | high
    message = Column(String(500), nullable=False)
    payload = Column(JSON, nullable=True)
    is_resolved = Column(Boolean, default=False)
    n8n_triggered = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    farm = relationship("Farm", back_populates="alerts")
