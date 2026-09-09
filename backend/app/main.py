from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.meeting import (
    MeetingRequest,
    MeetingResponse
)

from app.agents.meeting_agent import MeetingAgent

from app.schemas.competitor import (
    CompetitorRequest,
    CompetitorResponse
)

from app.agents.competitor_agent import CompetitorAgent


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


competitor_agent = CompetitorAgent()

@app.post(
    "/api/competitor/analyze",
    response_model=CompetitorResponse
)
def analyze_competitors(
    request: CompetitorRequest
):
    """
    Analyze recent competitor updates.

    The agent searches for recent information,
    filters noise and duplicates, categorizes
    meaningful updates, and generates an
    intelligence brief.
    """

    try:
        return competitor_agent.analyze(request)

    except Exception as e:
        print(f"Competitor agent error: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail="Failed to analyze competitor updates."
        )