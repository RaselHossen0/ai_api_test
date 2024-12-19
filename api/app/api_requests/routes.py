# app/api_requests/routes.py
from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Dict
import pandas as pd
from app.database import apis_collection
from app.api_requests.utils import generate_script
from app.api_requests.utils import generate_script
from app.database import collection
from app.api_testing_save.utils import retrieve_api_details

from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
import base64
import requests

router = APIRouter()

# Model to receive GitHub details
class GitHubDetails(BaseModel):
    owner: str
    repo: str
    access_token: str

# Model to receive the script to export
class ExportScript(BaseModel):
    file_name: str
    script_content: str
    owner: str

@router.post("/upload_api_requests")
async def upload_api_requests(
    file: UploadFile = File(...),
    language: str = "python",
    framework: str = "postman"
):
    if not (file.filename.endswith(".csv") or file.filename.endswith(".json")):
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a CSV or JSON file.")

    # Read the uploaded file
    api_requests = pd.read_csv(file.file) if file.filename.endswith(".csv") else pd.read_json(file.file)

    # Generate test scripts for each API request
    scripts = {}
    for index, row in api_requests.iterrows():
        script = generate_script(row.to_dict(), language, framework)
        scripts[f"script_{index}"] = script

    # Store the API request details in MongoDB
    for _, req in api_requests.iterrows():
        apis_collection.insert_one(req.to_dict())

    return scripts


@router.post("/generate_script")
async def generate_script_by_id(

    api_id: str,
    language: str = "python",
    framework: str = "postman"
):
    try:
        # Retrieve the API details using the given api_id
        api_detail = await retrieve_api_details(api_id)
        if not api_detail:
            raise HTTPException(status_code=404, detail="API details not found.")

        # Generate the script based on language and framework
        script = generate_script(api_detail[0], language, framework)
        return {"script": script}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate script: {str(e)}")
   

@router.post("/save_github_details")
async def save_github_details(details: GitHubDetails):
    # Save GitHub details to MongoDB, updating if already present
    result = collection.update_one(
        {"owner": details.owner, "repo": details.repo},
        {"$set": {"access_token": details.access_token}},
        upsert=True
    )
    if result.modified_count > 0 or result.upserted_id:
        return {"message": "GitHub details saved successfully"}
    raise HTTPException(status_code=500, detail="Failed to save GitHub details")


@router.get("/get_github_details")
async def get_github_details(owner: str):
    print(owner)
    # Fetch GitHub details from MongoDB
    github_details = collection.find_one({"owner": owner})
    if not github_details:
        raise HTTPException(status_code=404, detail="GitHub details not found")
    return {
        "owner": github_details["owner"],
        "repo": github_details["repo"],
        "access_token": github_details["access_token"]
    }


@router.put("/edit_github_details")
async def edit_github_details(details: GitHubDetails):
    print(details)
    # Update existing GitHub details in MongoDB
    result = collection.update_one(
        {"owner": details.owner},
        {"$set": {"access_token": details.access_token, "repo": details.repo}}
    )
    print(result.modified_count)
    if result.modified_count > 0:
        return {"message": "GitHub details updated successfully"}
    
    raise HTTPException(status_code=500, detail="Failed to update GitHub details")
def extract_repo_details(repo_url):
    print(f"Extracting details from URL: {repo_url}")
    
    # Remove .git extension if present, but do it more carefully
    if repo_url.endswith('.git'):
        repo_url = repo_url[:-4]  # Remove exactly '.git'
    print(f"Repo URL after removing '.git': {repo_url}")
    
    # Split the URL and get the last two parts
    parts = repo_url.split('/')
    print(f"URL parts: {parts}")
    
    if len(parts) < 2:
        raise HTTPException(status_code=400, detail="Invalid GitHub repository URL")

    owner = parts[-2]  # Second to last part is the owner
    repo = parts[-1]   # Last part is the repo name
    
    return owner, repo
@router.post("/export_script")
async def export_script(export: ExportScript):
    # Retrieve GitHub details from MongoDB
    github_details = collection.find_one({"owner": export.owner})
    print(f"GitHub Details: {github_details}")
    
    if github_details is None:
        raise HTTPException(status_code=404, detail="GitHub details not found")
    
    # Extract owner and repo from the URL
    try:
        owner, repo = extract_repo_details(github_details['repo'])
    except HTTPException as e:
        raise e  # Raise if the URL extraction failed

    print(f"Owner: {owner}, Repo: {repo}")
    
    # Prepare the API request to GitHub
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{export.file_name}"
    print(f"GitHub API URL: {url}")
    
    headers = {"Authorization": f"Bearer {github_details['access_token']}"}
    content = base64.b64encode(export.script_content.encode()).decode("utf-8")
    data = {
        "message": f"Automated commit of {export.file_name}",
        "content": content,
        "branch": "main"
    }

    # Send the request to create/update the file in GitHub
    response = requests.put(url, headers=headers, json=data)
    print(f"GitHub API Response: {response.status_code}, {response.text}")
    
    if response.status_code == 201 or response.status_code == 200:
        return {"message": f"File '{export.file_name}' committed successfully"}
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to export script to GitHub: {response.json().get('message', 'Unknown error')}"
        )