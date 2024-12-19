# app/api_requests/utils.py
from typing import Dict
import ast
from app.generative_ai.config import model, logger
def generate_script(api_request: Dict, language: str, framework: str):
    # Map the fields from the provided structure to the expected prompt
    api_name = api_request.get("api_name", "Unnamed API")
    url = api_request.get("api_url", "")
    method = api_request.get("http_method", "GET")
    headers = api_request.get("headers", {})
    payload = api_request.get("payload", {})
    expected_status = api_request.get("expected_status", 200)
    auth = api_request.get("auth", None)

    # Construct a prompt for Gemini that enforces real-life testing scenarios
    prompt = f"""
Generate a comprehensive API test script in {language} using {framework} to simulate real-world testing scenarios.
The script should test the API with various conditions and provide a report with the results.

API Details:
- Name: {api_name}
- URL: {url}
- HTTP Method: {method}
- Headers: {headers}
- Payload: {payload}
- Expected Status Code: {expected_status}
- Auth: {auth}

Key Testing Scenarios:
1. **Valid Request**: Test the API with valid input and ensure the status code is {expected_status}.
2. **Invalid Method**: Test the API with an unsupported HTTP method (e.g., POST if only GET is supported) and ensure the response is handled correctly (e.g., 405 Method Not Allowed).
3. **Missing Parameters**: Test the API with missing or incomplete parameters and check if the response contains the appropriate error message (e.g., 400 Bad Request).
4. **Boundary Testing**: Test the API with edge-case values, such as very large inputs, very small inputs, or values at the limit of what the API should accept.
5. **Authentication**: If authentication is required, ensure that the script tests the API with both valid and invalid credentials to verify proper authorization.
6. **Rate Limiting**: Simulate multiple consecutive requests to check how the API handles rate limiting and ensure it responds with the appropriate status code (e.g., 429 Too Many Requests).
7. **Load Testing**: Simulate a high number of concurrent requests to verify the API's ability to handle load and check for performance issues like timeouts or slow responses.
8. **Response Validation**: Verify that the response body matches the expected format and contains the correct data, including checking the content type and headers.
9. **Security**: Test the API for common security vulnerabilities, such as SQL injection, cross-site scripting (XSS), and improper authorization handling.

Ensure the script is modular, reusable, and easy to understand. It should also include appropriate assertions and logs for validation.

Please provide only the code in response, formatted as per {framework} standards.
"""

    try:
        chat = model.start_chat(history=[])
        response = chat.send_message(prompt)
        to_return = response.text.strip()

        # Extract the code block from the response
        if "```" in to_return:
            to_return = to_return.split("```")[1].strip()

        return to_return  # Return the script text, cleaned of extra whitespace
    except Exception as e:
        logger.error(f"Failed to generate script: {str(e)}")
        return f"Failed to generate script: {str(e)}"


