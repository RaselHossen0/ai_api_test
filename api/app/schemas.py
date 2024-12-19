# app/schemas.py
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from enum import Enum
from bson import ObjectId


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class User(BaseModel):
    id: Optional[str] = None  # This will be set automatically by MongoDB
    name: str
    email: Optional[str] = None
    disabled: Optional[bool] = None

    class Config:
        json_encoders = {ObjectId: str}


class UserCreate(BaseModel):
    name: str
    email: Optional[str] = None
    disabled: Optional[bool] = False
    password: str  # Include password here for hashing


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None  # Optional password field

    class Config:
        orm_mode = True

class UserInDB(User):
    hashed_password: str
    id: Optional[str] = None  # Add id as an optional field
    
class OAuth2PasswordRequestFormEmail(BaseModel):
    email: str
    password: str

class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

class APIRequest(BaseModel):
    url: HttpUrl
    method: HttpMethod
    headers: Optional[Dict[str, str]] = None
    query_params: Optional[Dict[str, str]] = None
    use_default_payload: bool = True
    custom_payload: Optional[Dict[str, Any]] = None

class APIResponse(BaseModel):
    payload: Dict[str, Any]
    status_code: int
    response_data: Any
    headers: Dict[str, str]

class APIDetails(BaseModel):
    api_name: str
    api_url: HttpUrl
    http_method: HttpMethod
    user_id: str  # New field for user ID
class APIDetailsForScript(BaseModel):
    api_url: str
    http_method: str
    headers: Optional[Dict[str, str]] = None
    parameters: Optional[Dict[str, Any]] = None
    payload: Optional[Dict[str, Any]] = None
class APIDetailsResponse(BaseModel):
    id: str
    api_name: str
    api_url: HttpUrl
    http_method: str
    user_id: str
    payload: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    created_at: Optional[str] = None
    
   

class BulkAPIText(BaseModel):
    api_list: str  # For pasting API list

class BulkAPIList(BaseModel):
    api_list: List[APIDetails]  # This accepts a list of APIDetails


# app/models.py


class APIDetails(BaseModel):
    api_name: str
    api_url: str
    http_method: str
    headers: Optional[Dict[str, str]] = None
    parameters: Optional[Dict[str, Any]] = None
    payload: Optional[Dict[str, Any]] = None
    user_id: str

class TestCase(BaseModel):
    description: str
    payload: Dict[str, Any]
    expected_status: int
    test_type: str

class TestExecutionRequest(BaseModel):
    framework: str
    parallel_execution: bool = False
    schedule: Optional[str] = None  # e.g., cron expression for scheduling

class TestScriptResponse(BaseModel):
    script: str

class ExecutionStatusResponse(BaseModel):
    execution_id: str
    status: str
    logs: List[str]