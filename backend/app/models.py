import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class RoleEnum(str, enum.Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"


class SeverityEnum(str, enum.Enum):
    SEV1 = "SEV1"
    SEV2 = "SEV2"
    SEV3 = "SEV3"
    SEV4 = "SEV4"


class StatusEnum(str, enum.Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"


class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    users = relationship("User", back_populates="organization")
    services = relationship("Service", back_populates="organization")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.MEMBER)
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    organization = relationship("Organization", back_populates="users")


class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    organization = relationship("Organization", back_populates="services")
    releases = relationship(
        "Release", back_populates="service", cascade="all, delete-orphan")
    incidents = relationship(
        "Incident", back_populates="service", cascade="all, delete-orphan")


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
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    service = relationship("Service", back_populates="incidents")
    release = relationship("Release", back_populates="incidents")
    updates = relationship("IncidentUpdate", back_populates="incident")
    assigned_to = relationship("User")


class IncidentUpdate(Base):
    __tablename__ = "incident_updates"
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="updates")
