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
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only admins can create projects")

    new_project = Project(
        name=project.name,
        repo_url=project.repo_url,
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

# =====================================================
# DELETE PROJECT (Admin only)
# =====================================================

@router.delete("/{project_id}", status_code=200)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a project (Admin only)
    """

    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Only admins can delete projects"
        )

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    db.delete(project)
    db.commit()

    return {"message": "Project deleted successfully"}

# =====================================================
# Get Project By ID (Admin only)
# =====================================================

@router.get("/{project_id}", response_model=ProjectOut)
def get_project_by_id(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Only admins can view project details"
        )

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return project


