"""Module for the main index route"""

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/")
async def index(request: Request):
    """
    Returns the index page with search UIs for enabled endpoints.
    """
    # TODO: return Jinja2 template response
