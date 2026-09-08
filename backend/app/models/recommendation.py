import uuid
import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class Recommendation(Base):
    """Stores fertilizer / irrigation / insight-type recommendations
    (distinct from raw ML predictions) for history + n8n triggers."""
    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    farm_id = Column(String(36), ForeignKey("farms.id"), nullable=False, index=True)

    category = Column(String(50), nullable=False)  # fertilizer | irrigation | insight
    title = Column(String(200), nullable=False)
    detail = Column(JSON, nullable=True)
    severity = Column(String(20), default="info")  # info | low | medium | high

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    farm = relationship("Farm", back_populates="recommendations")
