from fastapi import FastAPI, HTTPException, UploadFile, File, Form
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

from app.schemas.website_qa import (
    WebsiteQARequest,
    WebsiteQAResponse
)

from app.agents.website_qa_agent import (
    WebsiteQAAgent
)

import csv
import io


from app.schemas.lead_qualification import (
    ICP,
    LeadQualificationResponse
)

from app.agents.lead_qualification_agent import (
    LeadQualificationAgent
)


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


@app.post(
    "/api/website-qa/analyze",
    response_model=WebsiteQAResponse
)
def analyze_website(
    request: WebsiteQARequest
):

    """
    Analyze a website for broken links,
    missing images, SEO problems and
    potential UI/content issues.
    """

    try:

        agent = WebsiteQAAgent()

        result = agent.analyze(
            request
        )

        return result

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        print(
            f"Website QA agent error: {str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to analyze website."
            )
        )


lead_qualification_agent = LeadQualificationAgent()

@app.post(
    "/api/lead-qualification/analyze",
    response_model=LeadQualificationResponse
)
async def analyze_leads(
    file: UploadFile = File(...),
    icp: str = Form(...)
):
    """
    Analyze leads from a CSV file against
    a predefined Ideal Customer Profile (ICP).
    """

    try:
        # Validate CSV file
        if not file.filename or not file.filename.lower().endswith(".csv"):
            raise HTTPException(
                status_code=400,
                detail="Please upload a CSV file."
            )

        # Read uploaded CSV
        contents = await file.read()

        try:
            csv_text = contents.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="CSV file must be UTF-8 encoded."
            )

        reader = csv.DictReader(io.StringIO(csv_text))

        if not reader.fieldnames:
            raise HTTPException(
                status_code=400,
                detail="CSV file has no header row."
            )

        leads = []

        for row in reader:
            lead = {}

            for key, value in row.items():
                if key is None:
                    continue

                key = key.strip()

                if isinstance(value, str):
                    value = value.strip()

                lead[key] = value

            # Ignore completely empty rows
            if any(value not in ("", None) for value in lead.values()):
                leads.append(lead)

        if not leads:
            raise HTTPException(
                status_code=400,
                detail="CSV file contains no leads."
            )

        # Parse ICP JSON
        try:
            icp_data = ICP.model_validate_json(icp)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid ICP data."
            )

        # Run agent
        result = lead_qualification_agent.analyze(
            leads=leads,
            icp=icp_data
        )

        return result

    except HTTPException:
        raise

    except Exception as e:
        print(
            f"Lead qualification agent error: {str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to analyze leads."
        )