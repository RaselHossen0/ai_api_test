# Project Setup and Run Instructions

## Prerequisites
- Python 3.8+
- Node.js 14+
- npm 6+
- `pip` (Python package installer)

## Backend (FastAPI)

### Setup

1. **Clone the repository**:
    ```bash
    git clone https://github.com/RaselHossen0/ai_api_test
    cd api
    ```

2. **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### Run

1. **Navigate to the `app` directory**:
    ```bash
    cd app
    ```

2. **Run the FastAPI server**:
    ```bash
    uvicorn main:app --reload
    ```

3. **Access the API documentation**:
    Open your browser and navigate to `http://127.0.0.1:8000/docs` for the interactive API documentation.

## Frontend (React)

### Setup

1. **Navigate to the [frontend](http://_vscodecontentref_/0) directory**:
    ```bash
    cd ../frontend
    ```

2. **Install dependencies**:
    ```bash
    npm install
    ```

### Run

1. **Start the React development server**:
    ```bash
    npm start
    ```

2. **Access the React application**:
    Open your browser and navigate to `http://localhost:3000`.

## Notes

- Ensure that both the backend and frontend servers are running simultaneously for full functionality.
- If you encounter any issues, check the terminal output for error messages and ensure all dependencies are installed correctly.