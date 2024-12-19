# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.routes import router as auth_router
from app.users.routes import router as users_router
#from app.generative_ai.routes import router as generative_ai_router

from app.api_testing_save.routes import router as api_testing_save_router
from app.api_management.routes import router as api_management_router
from app.api_requests.routes import router as api_requests_router


app = FastAPI(title="API Upload Service")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth")
app.include_router(users_router, prefix="/users")
#app.include_router(api_tester_router, prefix="/api-tester")

app.include_router(api_testing_save_router, prefix="/api_testing_save")
#app.include_router(generative_ai_router, prefix="/api", tags=["generative_ai"])
app.include_router(api_management_router, prefix="/api_management")
app.include_router(api_requests_router, prefix="/api/script")


