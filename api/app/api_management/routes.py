# app/api_management/routes.py
import asyncio
import uuid
from bson import ObjectId
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List
from app.schemas import APIDetails, BulkAPIText , BulkAPIList , APIDetailsResponse
from app.api_management.utils import store_api_details, parse_csv_content, parse_json_content
from app.database import collection  # MongoDB collection

router = APIRouter()

@router.post("/upload/individual", response_model=dict)
async def upload_individual_api(api_details: APIDetails):
    try:
        api_dict = api_details.dict()
        stored_api = await store_api_details(api_dict)
        return {"status": "success", "message": "API details stored successfully", "api": stored_api}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/file")
async def upload_file(file: UploadFile = File(...), user_id: str = Form(...)):
    try:
        content = await file.read()
        content_str = content.decode('utf-8-sig')  # Handle BOM if present

        if not content_str.strip():
            raise HTTPException(status_code=400, detail="File is empty")

        if file.filename.endswith('.csv'):
            apis = await parse_csv_content(content_str, user_id)
        elif file.filename.endswith('.json'):
            apis = await parse_json_content(content_str, user_id)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload CSV or JSON file.")

        if not apis:
            return {
                "status": "warning",
                "message": "No valid API details found in the file",
                "apis": []
            }

        # Store the APIs
        stored_apis = []
        for api in apis:
            stored_api = await store_api_details(api)
            stored_apis.append(stored_api)

        return {
            "status": "success",
            "message": f"Successfully stored {len(stored_apis)} API details",
            "apis": stored_apis
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/upload/text")
async def upload_text(data: BulkAPIList):
    """
    Upload API details via pasted text (JSON format)
    """
    try:
        apis = data.api_list  # Now this will directly use the list of APIs
        stored_apis = []
        
        for api in apis:
            stored_api = await store_api_details(api.dict())
            stored_apis.append(stored_api)

        return {
            "status": "success",
            "message": f"Successfully stored {len(stored_apis)} API details",
            "apis": stored_apis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/apis", response_model=List[APIDetailsResponse])
async def get_apis_by_user(user_id: str):
    try:
        api_docs = list(collection.find({"user_id": user_id}))
        # print(api_docs)
        api_tasks = [convert_to_api_details_response(api_doc) for api_doc in api_docs]
        apis = await asyncio.gather(*api_tasks)
        return apis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def convert_to_api_details_response(api_doc: dict) -> APIDetailsResponse:
    api_doc["id"] = str(api_doc.pop("_id"))
    api_doc["payload"] = api_doc.get("payload", None)
    api_doc["parameters"] = api_doc.get("parameters", None)
    api_doc["headers"] = api_doc.get("headers", None)
    created_at = api_doc.get("created_at", None)
    api_doc["created_at"] = created_at.isoformat() if created_at else None
    return APIDetailsResponse(**api_doc)
    
# Update the delete endpoint to work with UUID strings
@router.delete("/apis/{api_id}")
async def delete_api(api_id: str):
    try:
        # Validate UUID format
        try:
            uuid.UUID(api_id)  # This will raise ValueError if invalid UUID
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid API ID format. Must be a valid UUID.")
        
        # Execute delete operation using string ID directly
        result = collection.delete_one({"_id": api_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="API not found")
            
        return {"status": "success", "message": "API deleted successfully"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
