from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # ADMIN or TECH_LEAD
    created_at = Column(DateTime, default=datetime.utcnow)

    projects = relationship("UserProject", back_populates="user")


class UserProject(Base):
    __tablename__ = "user_projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    assigned_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="projects")
    project = relationship("Project", back_populates="users")

    # ============================
# Project Model
# ============================
# Stores GitHub repository information
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, nullable=False)
    github_org = Column(String, nullable=False)
    repo_name = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)


# ============================
# Project Assignment Model
# ============================
# Maps Tech Leads to Projects
class ProjectAssignment(Base):
    __tablename__ = "project_assignments"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    tech_lead_id = Column(Integer, ForeignKey("users.id"))

    assigned_at = Column(DateTime, default=datetime.utcnow)

