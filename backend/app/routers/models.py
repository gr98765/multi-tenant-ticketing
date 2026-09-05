from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
import enum


class SeverityEnum(str, enum.Enum):
    SEV1 = "SEV1"
    SEV2 = "SEV2"
    SEV3 = "SEV3"
    SEV4 = "SEV4"


class StatusEnum(str, enum.Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"


class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    releases = relationship("Release", back_populates="service")
    incidents = relationship("Incident", back_populates="service")


class Release(Base):
    __tablename__ = "releases"
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"))
    version = Column(String, nullable=False)
    deployed_at = Column(DateTime, default=datetime.utcnow)

    service = relationship("Service", back_populates="releases")
    incidents = relationship("Incident", back_populates="release")


class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    severity = Column(Enum(SeverityEnum), default=SeverityEnum.SEV3)
    status = Column(Enum(StatusEnum), default=StatusEnum.OPEN)
    service_id = Column(Integer, ForeignKey("services.id"))
    release_id = Column(Integer, ForeignKey("releases.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    service = relationship("Service", back_populates="incidents")
    release = relationship("Release", back_populates="incidents")
    updates = relationship("IncidentUpdate", back_populates="incident")


class IncidentUpdate(Base):
    __tablename__ = "incident_updates"
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="updates")
