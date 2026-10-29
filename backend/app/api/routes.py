"""Version 1 API endpoints.

Every route here is served under the /api/v1 prefix (set in app/main.py).
"""

from fastapi import APIRouter, status

APP_NAME = "OpsIQ"

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
def api_root():
    """Welcome message with a pointer to the interactive documentation."""
    return {
        "message": f"Welcome to the {APP_NAME} API.",
        "docs": "/docs",
    }


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Report that the API is running.

    This does not read the dataset, so it stays fast and never exposes data.
    """
    return {
        "app": APP_NAME,
        "status": "healthy",
    }
