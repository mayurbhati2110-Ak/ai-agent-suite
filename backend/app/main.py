from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.meeting import (
    MeetingRequest,
    MeetingResponse
)

from app.agents.meeting_agent import MeetingAgent


app = FastAPI(
    title="AI Agent Suite",
    description="Reusable backend for AI-powered agents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "AI Agent Suite Backend is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# Create agent instance
meeting_agent = MeetingAgent()


@app.post(
    "/api/meeting/analyze",
    response_model=MeetingResponse
)
def analyze_meeting(request: MeetingRequest):

    try:
        result = meeting_agent.analyze(
            transcript=request.transcript
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while analyzing the meeting."
        )