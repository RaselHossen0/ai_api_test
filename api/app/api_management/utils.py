# app/api_management/utils.py
import csv
import json
import io
import uuid
from datetime import datetime
from typing import List
from app.database import collection  # MongoDB collection
from fastapi import HTTPException
from app.schemas import HttpMethod
from fastapi.encoders import jsonable_encoder

# In store_api_details function (no changes needed as it's already using UUID)
async def store_api_details(api_details: dict):
    api_details = jsonable_encoder(api_details)
    api_details["_id"] = str(uuid.uuid4())
    api_details["created_at"] = datetime.utcnow()
    
    result = collection.insert_one(api_details)
    return api_details


async def parse_csv_content(content: str, user_id: str) -> List[dict]:
    apis = []
    csv_reader = csv.DictReader(io.StringIO(content))
    required_fields = ["api_name", "api_url", "http_method"]
    
    # Validate CSV headers
    headers = csv_reader.fieldnames
    if not headers or not all(field in headers for field in required_fields):
        raise ValueError(f"CSV must contain all required fields: {', '.join(required_fields)}")
    
    for row in csv_reader:
        # Skip empty rows
        if not any(row.values()):
            continue
            
        # Validate required fields are not empty
        if not all(row.get(field, '').strip() for field in required_fields):
            continue
            
        api = {
            "api_name": row["api_name"].strip(),
            "api_url": row["api_url"].strip(),
            "http_method": row["http_method"].strip().upper(),
            "user_id": user_id,
            "_id": str(uuid.uuid4())  # Generate a unique ID
        }
        
        # Validate HTTP method
        if api["http_method"] not in HttpMethod.__members__:
            raise ValueError(f"Invalid HTTP method: {api['http_method']}")
            
        apis.append(api)
    
    return apis

async def parse_json_content(content: str, user_id: str) -> List[dict]:
    try:
        data = json.loads(content)
        apis = []
        
        # Handle both single object and array formats
        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            raise ValueError("JSON content must be an object or an array of API details")
            
        required_fields = ["api_name", "api_url", "http_method"]
        
        for api in data:
            # Validate required fields
            if not all(key in api and api[key] for key in required_fields):
                raise ValueError(f"Missing or empty required fields. Required: {', '.join(required_fields)}")
                
            processed_api = {
                "api_name": str(api["api_name"]).strip(),
                "api_url": str(api["api_url"]).strip(),
                "http_method": str(api["http_method"]).strip().upper(),
                "user_id": user_id,
                "_id": str(uuid.uuid4())  # Generate a unique ID
            }
            
            # Validate HTTP method
            if processed_api["http_method"] not in HttpMethod.__members__:
                raise ValueError(f"Invalid HTTP method: {processed_api['http_method']}")
                
            apis.append(processed_api)
            
        return apis
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")