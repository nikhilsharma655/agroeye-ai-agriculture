import uuid
import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class SoilRecord(Base):
    __tablename__ = "soil_records"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    farm_id = Column(String(36), ForeignKey("farms.id"), nullable=False, index=True)

    nitrogen = Column(Float, nullable=True)
    phosphorus = Column(Float, nullable=True)
    potassium = Column(Float, nullable=True)
    ph = Column(Float, nullable=True)
    moisture = Column(Float, nullable=True)
    soil_type = Column(String(50), nullable=True)

    recorded_at = Column(DateTime, default=datetime.datetime.utcnow)

    farm = relationship("Farm", back_populates="soil_records")
