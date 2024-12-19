# API Testing Platform

This project provides a platform to upload API details, generate test cases, and perform automated testing. It allows both individual and bulk API uploads, customizable test cases, and a Swagger UI interface for easy API interaction.

## Features

- **Individual and Bulk API Uploads**: Upload APIs one by one or in batches.
- **Automated Test Case Generation**: Generate positive, negative, and boundary test cases for uploaded APIs using AI.
- **API Testing**: Execute tests asynchronously and review detailed results, including response data, status codes, and success criteria.
- **CI/CD Integration**: Integrate with GitHub for continuous integration and delivery.
- **Reports**: Generate detailed HTML/PDF test reports for analysis.

## Requirements

- **Python**: 3.7+
- **Database**: MongoDB
- **Dependencies**: Listed in `requirements.txt`

## Setup Instructions

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**: Configure your environment variables for MongoDB and other credentials if needed.

4. **Run the FastAPI app**:

   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access Swagger Documentation**:
   Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in a browser to interact with the API endpoints.

## API Usage Examples

### 1. Individual API Upload

Use this format to upload details of a single API:

```json
{
  "api_name": "User Registration",
  "api_url": "https://api.example.com/auth/register",
  "http_method": "POST"
}
```

### 2. Bulk API Upload

To upload multiple APIs at once, use this format:

```json
{
  "api_list": [
    {
      "api_name": "Get Comments",
      "api_url": "https://api.example.com/posts/{id}/comments",
      "http_method": "GET"
    },
    {
      "api_name": "Add Comment",
      "api_url": "https://api.example.com/posts/{id}/comments",
      "http_method": "POST"
    },
    {
      "api_name": "Update Comment",
      "api_url": "https://api.example.com/comments/{id}",
      "http_method": "PUT"
    },
    {
      "api_name": "Delete Comment",
      "api_url": "https://api.example.com/comments/{id}",
      "http_method": "DELETE"
    }
  ]
}
```

### 3. API Testing Example

Submit an API testing request, including headers and payload data:

```json
{
    "api_name": "check",
    "api_url": "http://localhost:8000/api/auth/create-user",
    "http_method": "POST",
    "headers": {
        "Content-Type": "application/json",
        "Authorization": "Bearer <token>"
    },
    "parameters": null,
    "payload": {
        "email": "user@example.com",
        "password": "password123",
        "confirmPass": "password123",
        "name": "John Doe",
        "dob": "1990-01-01",
        "gender": "Male",
        "userType": "user",
        "departmentId": 3,
        "registeredFrom": "Platform",
        "phone": "123-456-7890"
    },
    "user_id": "67290812fa06ee7cee84cf79"
}
{
    "api_url": "http://localhost:8000/api/auth/create-user",
    "http_method": "POST",
    "headers": {
        "Content-Type": "application/json",
        "Authorization": "Bearer <token>"
    },
    "parameters": null,
    "payload": {
        "email": "user@example.com",
        "password": "password123",
        "confirmPass": "password123",
        "name": "John Doe",
        "dob": "1990-01-01",
        "gender": "Male",
        "userType": "user",
        "departmentId": 3,
        "registeredFrom": "Platform",
        "phone": "123-456-7890"
    }
}
{
    "api_url": "https://api-tau-teal.vercel.app/users/create",
    "http_method": "POST",
    "headers": {
        "Content-Type": "application/json"

    },
    "parameters": null,
    "payload": {
  "name": "string",
  "email": "string",
  "disabled": false,
  "password": "string"
}
}
```

## Helper Functions

The helper functions generate the appropriate test scripts for each language and framework. The examples provided include:

- **python with postman**
- **javaScript with cypress**
- **java with junit**
