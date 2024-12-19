# app/api_testing/utils.py
from typing import List, Dict, Optional, Any
import httpx
import json
from pydantic import BaseModel
from fastapi import HTTPException
from app.generative_ai.config import model, logger




import uuid
from datetime import datetime

from app.database import collection  # MongoDB collection


from fastapi.encoders import jsonable_encoder

class TestCase(BaseModel):
    description: str
    payload: Dict[str, Any]
    expected_status: int
    test_type: str  # positive, negative, boundary

async def generate_test_cases(details) -> List[TestCase]:
    prompt = f"""
        Generate test cases in JSON format for the following API request. Include positive, negative, and boundary test cases.

        API Details:
        - HTTP Method: {details.http_method}
        - Endpoint: {details.api_url}
        - Headers: {details.headers}
        - Parameters: {details.parameters}
        - Sample Payload: {json.dumps(details.payload, indent=2)}

        Each test case should include **realistic and practical data values** for fields like email addresses, names, phone numbers, and other commonly used fields in APIs. Avoid placeholder terms like "example" or "test". Use realistic examples such as:
        - Email: "john.doe@yahoo.com", "rasel@gmail.com", etc.
        - Name: "John Doe", "Jane O'Connor", "Dr. Emily Watson", etc.
        - Passwords: Use realistic examples like "StrongPass123!", "WeakPassword", or "abc".
        - Special Characters: Include examples such as "John@Doe!" or "Company_Name#42".
        - Numbers: Use realistic values such as "12345", "9999999999", or "-10".

        Return a **strictly valid JSON array** of test cases, where each test case follows this structure:
        [
        {{
            "description": "Test case description",
            "payload": {{payload_data}},
            "expected_status": expected_http_status_code,
            "test_type": "positive|negative|boundary"
        }},
        ...
        ]

        Focus on these common scenarios:
        1. Valid data (positive)
        2. Missing required fields (negative)
        3. Invalid data types (negative)
        4. Boundary values for fields (boundary, e.g., maximum lengths, special characters, or empty strings)
        5. Realistic special characters in strings (negative)
        6. Empty/null values (negative)
        7. Large data payloads (boundary, e.g., long names or emails)

        Ensure all examples are **real-world applicable**. Only return the JSON array. Do not include any additional text or explanation in the response.And give at least 10 test cases.
        """
    try:
        # Initiate the chat and send the prompt
        chat = model.start_chat(history=[])
        response = chat.send_message(prompt)

        # Extract and validate JSON
        response_text = response.text.strip()
        print(response_text)
        try:
            # replace ```json with empty string
             response_text = response_text.replace("```json", "").replace("```", "")
             
            
            # Replace invalid placeholder values like `"a".repeat(256)`
            
          
             test_cases_data = json.loads(response_text)  # Parse as JSON
             if not isinstance(test_cases_data, list):
                raise ValueError("Response is not a valid JSON array.")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON response from model: {response_text}")
            raise HTTPException(status_code=500, detail="Model response was not valid JSON")

        # Validate each test case against the expected structure
        try:
            test_cases = [TestCase(**case) for case in test_cases_data]
        except Exception as e:
            logger.error(f"Invalid test case structure: {str(e)}")
            raise HTTPException(status_code=422, detail=f"Test case validation error: {str(e)}")

        return test_cases

    except HTTPException as e:
        # Re-raise known HTTP exceptions
        raise e
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Error generating test cases: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
async def make_request(
    client: httpx.AsyncClient,
    url: str,
    method: str,
    headers: Optional[Dict[str, str]],
    params: Optional[Dict[str, str]],
    test_case: TestCase
):
    try:
        response = await client.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=test_case.payload,
            timeout=30.0
        )
        
        return {
            "test_case": test_case,
            "status_code": response.status_code,
            "response_data": response.json() if response.text else None,
            "headers": dict(response.headers),
            "success": response.status_code == test_case.expected_status
        }
    except Exception as e:
        logger.error(f"Request failed for test case '{test_case.description}': {str(e)}")
        return {
            "test_case": test_case,
            "status_code": 500,
            "response_data": {"error": str(e)},
            "headers": {},
            "success": False
        }

# In store_api_details function (no changes needed as it's already using UUID)
async def store_api_details(api_details: dict):
    api_details = jsonable_encoder(api_details)
    api_details["_id"] = str(uuid.uuid4())
    api_details["created_at"] = datetime.utcnow()
    
    result = collection.insert_one(api_details)
    return api_details

async def retrieve_api_details(api_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieve API details from the database.
    - If `api_id` is provided, fetch specific details.
    - If `api_id` is not provided, return all details.
    """
    if api_id:
        api_detail = collection.find_one({"_id": api_id})
        return [api_detail] if api_detail else []
    else:
        api_details = list(collection.find())
        return api_details