# app/projects.py
"""
Handles project creation, assignment, and retrieval.
Used by Admin and Tech Leads for dashboard access.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Project, User, UserProject
from app.auth import get_current_user
from app.schemas import ProjectCreate, ProjectOut

router = APIRouter(prefix="/projects", tags=["Projects"])


# =====================================================
# CREATE PROJECT (Admin only)
# =====================================================
@router.post("/", response_model=ProjectOut)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Admin creates a new project (GitHub repo).
    """

    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only admins can create projects")

    new_project = Project(
        project_name=project.project_name,
        github_org=project.github_org,
        repo_name=project.repo_name,
        created_by=current_user.id
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project


# =====================================================
# ASSIGN TECH LEAD TO PROJECT (Admin only)
# =====================================================
@router.post("/{project_id}/assign/{user_id}")
def assign_project(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Assign a tech lead to a project.
    """

    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only admins can assign projects")

    assignment = UserProject(
        project_id=project_id,
        user_id=user_id
    )

    db.add(assignment)
    db.commit()

    return {"message": "Tech Lead assigned successfully"}


# =====================================================
# GET PROJECTS (Admin / Tech Lead)
# =====================================================
@router.get("/", response_model=List[ProjectOut])
def get_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Admin → all projects
    Tech Lead → assigned projects only
    """

    if current_user.role == "ADMIN":
        return db.query(Project).all()

    # Tech Lead: only assigned projects
    projects = (
        db.query(Project)
        .join(UserProject)
        .filter(UserProject.user_id == current_user.id)
        .all()
    )

    return projects
