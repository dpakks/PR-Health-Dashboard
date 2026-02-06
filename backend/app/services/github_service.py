"""
GitHubService
--------------
Handles all communication with GitHub REST APIs.
This layer is independent of FastAPI routes and the database.
"""

import requests
from fastapi import HTTPException
from app.config import settings


class GitHubService:
    """
    Wrapper around GitHub REST API
    """

    BASE_URL = "https://api.github.com"

    def __init__(self):
        # Authorization header using GitHub token
        self.headers = {
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        }

    def test_connection(self):
        """
        Simple test call to verify GitHub authentication works
        """
        response = requests.get(
            f"{self.BASE_URL}/user",
            headers=self.headers
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail="Failed to authenticate with GitHub"
            )

        return response.json()

    def get_open_pull_requests(self, owner: str, repo: str):
        """
        Fetch open pull requests for a repository
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls"

        response = requests.get(
            url,
            headers=self.headers,
            params={"state": "open"}
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch pull requests from GitHub"
            )

        return response.json()
