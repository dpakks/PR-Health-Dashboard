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
from app.schemas import ProjectCreate, ProjectOut, PullRequestOut, UserResponse
from app.services.github_service import GitHubService
from datetime import datetime, timezone
from collections import defaultdict

STALE_DAYS = 7

router = APIRouter(prefix="/projects", tags=["Projects"])

# =====================================================
# CREATE PROJECT (Admin only)
# =====================================================
@router.post("/create", response_model=ProjectOut)
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
@router.get("/getAll", response_model=List[ProjectOut])
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

@router.get("/test/github")
def test_github():
    github = GitHubService()
    prs = github.get_open_pull_requests(
        owner="octocat",
        repo="Hello-World"
    )
    return prs

# =====================================================
# GET USERS ASSIGNED TO A PROJECT (ADMIN ONLY)
# =====================================================
@router.get("/{project_id}/users", response_model=List[UserResponse])
def get_users_assigned_to_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Fetch all users assigned to a project (Admin only)
    """

    # -------------------------------------------------
    # 1. Admin authorization
    # -------------------------------------------------
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Only admins can view project users"
        )

    # -------------------------------------------------
    # 2. Validate project
    # -------------------------------------------------
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # -------------------------------------------------
    # 3. Fetch assigned users
    # -------------------------------------------------
    users = (
        db.query(User)
        .join(UserProject, User.id == UserProject.user_id)
        .filter(UserProject.project_id == project_id)
        .all()
    )

    return users

# =====================================================
# REMOVE USER FROM PROJECT (ADMIN ONLY)
# =====================================================
@router.delete("/{project_id}/users/{user_id}", status_code=200)
def remove_user_from_project(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Remove a user from a project (Admin only)
    """

    # -------------------------------------------------
    # 1. Authorization
    # -------------------------------------------------
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Only admins can remove users from projects"
        )

    # -------------------------------------------------
    # 2. Check assignment exists
    # -------------------------------------------------
    assignment = db.query(UserProject).filter(
        UserProject.project_id == project_id,
        UserProject.user_id == user_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="User is not assigned to this project"
        )

    # -------------------------------------------------
    # 3. Delete assignment
    # -------------------------------------------------
    db.delete(assignment)
    db.commit()

    return {"message": "User removed from project successfully"}




# =====================================================
# GET OPEN PULL REQUESTS FOR A PROJECT
# =====================================================
@router.get("/{project_id}/pull-requests", response_model=list[PullRequestOut])
def get_project_pull_requests(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Fetch open pull requests for a project from GitHub.
    Admin → any project
    Tech Lead → only assigned projects
    Adds PR metrics: days_open & is_stale
    """

    # -------------------------------------------------
    # 1. Fetch project
    # -------------------------------------------------
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # -------------------------------------------------
    # 2. Authorization
    # -------------------------------------------------
    if current_user.role != "ADMIN":
        assignment = db.query(UserProject).filter(
            UserProject.project_id == project_id,
            UserProject.user_id == current_user.id
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to view this project"
            )

    # -------------------------------------------------
    # 3. Extract GitHub owner & repo
    # -------------------------------------------------
    repo_url = project.repo_url.rstrip("/")
    try:
        owner = repo_url.split("/")[-2]
        repo = repo_url.split("/")[-1]
    except IndexError:
        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub repository URL"
        )

    # -------------------------------------------------
    # 4. Fetch PRs from GitHub
    # -------------------------------------------------
    github = GitHubService()
    prs = github.get_open_pull_requests(owner=owner, repo=repo)

    # -------------------------------------------------
    # 5. Compute metrics
    # -------------------------------------------------
    now = datetime.now(timezone.utc)
    normalized_prs = []

    for pr in prs:
        created_at = datetime.fromisoformat(
            pr["created_at"].replace("Z", "+00:00")
        )

        days_open = (now - created_at).days

        normalized_prs.append({
            "id": pr["number"],
            "title": pr["title"],
            "author": pr["user"]["login"],
            "state": pr["state"],
            "source_branch": pr["head"]["ref"],
            "target_branch": pr["base"]["ref"],
            "created_at": created_at,
            "days_open": days_open,
            "is_stale": days_open > STALE_DAYS,
            "url": pr["html_url"]
        })

    return normalized_prs

@router.get("/{project_id}/pull-requests/summary")
def get_pr_summary(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    PR Summary Metrics:
    - Total open PRs
    - Stale PR count
    - Average days open
    - Oldest PR age
    """

    # -------------------------------------------------
    # 1. Fetch project
    # -------------------------------------------------
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # -------------------------------------------------
    # 2. Authorization
    # -------------------------------------------------
    if current_user.role != "ADMIN":
        assignment = db.query(UserProject).filter(
            UserProject.project_id == project_id,
            UserProject.user_id == current_user.id
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=403,
                detail="Not authorized"
            )

    # -------------------------------------------------
    # 3. Extract owner & repo
    # -------------------------------------------------
    repo_url = project.repo_url.rstrip("/")
    owner = repo_url.split("/")[-2]
    repo = repo_url.split("/")[-1]

    # -------------------------------------------------
    # 4. Fetch PRs
    # -------------------------------------------------
    github = GitHubService()
    prs = github.get_open_pull_requests(owner=owner, repo=repo)

    if not prs:
        return {
            "total_open_prs": 0,
            "stale_prs": 0,
            "average_days_open": 0,
            "oldest_pr_days": 0
        }

    # -------------------------------------------------
    # 5. Compute metrics
    # -------------------------------------------------
    now = datetime.now(timezone.utc)
    days_open_list = []

    for pr in prs:
        created_at = datetime.fromisoformat(
            pr["created_at"].replace("Z", "+00:00")
        )
        days_open = (now - created_at).days
        days_open_list.append(days_open)

    total_open_prs = len(prs)
    stale_prs = len([d for d in days_open_list if d > STALE_DAYS])
    average_days_open = round(sum(days_open_list) / total_open_prs)
    oldest_pr_days = max(days_open_list)

    return {
        "total_open_prs": total_open_prs,
        "stale_prs": stale_prs,
        "average_days_open": average_days_open,
        "oldest_pr_days": oldest_pr_days
    }

@router.get("/{project_id}/pull-requests/trends")
def get_pr_trends(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    PR Trend Metrics:
    - PRs opened per day
    - PRs opened per week
    """

    # -------------------------------------------------
    # 1. Fetch project
    # -------------------------------------------------
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # -------------------------------------------------
    # 2. Authorization
    # -------------------------------------------------
    if current_user.role != "ADMIN":
        assignment = db.query(UserProject).filter(
            UserProject.project_id == project_id,
            UserProject.user_id == current_user.id
        ).first()

        if not assignment:
            raise HTTPException(status_code=403, detail="Not authorized")

    # -------------------------------------------------
    # 3. Extract owner & repo
    # -------------------------------------------------
    repo_url = project.repo_url.rstrip("/")
    owner = repo_url.split("/")[-2]
    repo = repo_url.split("/")[-1]

    # -------------------------------------------------
    # 4. Fetch PRs from GitHub
    # -------------------------------------------------
    github = GitHubService()
    prs = github.get_open_pull_requests(owner=owner, repo=repo)

    # -------------------------------------------------
    # 5. Build trends
    # -------------------------------------------------
    daily_counts = defaultdict(int)
    weekly_counts = defaultdict(int)

    for pr in prs:
        created_at = datetime.fromisoformat(
            pr["created_at"].replace("Z", "+00:00")
        )

        day_key = created_at.strftime("%Y-%m-%d")
        week_key = f"{created_at.year}-W{created_at.isocalendar().week}"

        daily_counts[day_key] += 1
        weekly_counts[week_key] += 1

    return {
        "daily": dict(daily_counts),
        "weekly": dict(weekly_counts)
    }