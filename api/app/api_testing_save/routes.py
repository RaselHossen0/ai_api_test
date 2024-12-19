# app/api_testing/routes.py
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from app.api_testing_save.utils import generate_test_cases, make_request, store_api_details, retrieve_api_details
from pydantic import BaseModel, HttpUrl
import httpx
import asyncio

router = APIRouter()

class APIDetails(BaseModel):
    api_name: str  # New field for API name
    api_url: HttpUrl
    http_method: str
    headers: Optional[Dict[str, str]] = None
    parameters: Optional[Dict[str, Any]] = None
    payload: Optional[Dict[str, Any]] = None
    user_id: str  # New field for user ID
    is_previous: bool  # New field for previous API

@router.post("/test-api")
async def test_api(details: APIDetails) -> List[dict]:
    """
    Test an API with AI-generated test cases and return responses.
    """
    # Save API details
    try:
        api_dict = details.dict()
        if details.is_previous is False:
            await store_api_details(api_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store API details: {str(e)}")

    # Generate test cases
    try:
        test_cases = await generate_test_cases(details)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate test cases: {str(e)}")

    if not test_cases:
        raise HTTPException(status_code=400, detail="No test cases generated")

    # Execute test cases
    async with httpx.AsyncClient() as client:
        tasks = [
            make_request(client, str(details.api_url), details.http_method, details.headers, details.parameters, test_case)
            for test_case in test_cases
        ]
        responses = await asyncio.gather(*tasks)
        return responses

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@router.get("/api/details", response_model=List[dict])
async def get_api_details(api_id: Optional[str] = None):
    """
    Retrieve saved API details. If `api_id` is provided, fetch a specific API detail; otherwise, return all.
    """
    try:
        details = await retrieve_api_details(api_id)
        if not details:
            raise HTTPException(status_code=404, detail="API details not found")
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve API details: {str(e)}")
