# pylint: disable=too-few-public-methods
from datetime import datetime

from sqlalchemy import Float, Column, String, Integer, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PredictionTable(Base):
    """Implement table for storing features with corresponding predictions."""

    __tablename__ = "prediction_log"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.now)
    gender = Column(String)
    age = Column(Float)
    hypertension = Column(Integer)
    heart_disease = Column(Integer)
    smoking_history = Column(String)
    bmi = Column(Float)
    hba1c_level = Column(Float)
    blood_glucose_level = Column(Integer)
    prediction = Column(Integer)
    model_version = Column(String)
