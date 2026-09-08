import uuid
import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class Prediction(Base):
    """Generic store for any ML model output (crop rec, yield, disease, etc.)
    so historical analytics/dashboards can query a single table."""
    __tablename__ = "predictions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    farm_id = Column(String(36), ForeignKey("farms.id"), nullable=False, index=True)

    prediction_type = Column(String(50), nullable=False)  # crop_recommendation | yield | disease_risk
    model_name = Column(String(80), nullable=True)
    input_payload = Column(JSON, nullable=True)
    output_payload = Column(JSON, nullable=True)
    confidence = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    farm = relationship("Farm", back_populates="predictions")
