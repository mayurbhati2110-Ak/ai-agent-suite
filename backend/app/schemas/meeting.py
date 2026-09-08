from typing import Optional, List
from pydantic import BaseModel, Field


# -----------------------------
# INPUT SCHEMA
# -----------------------------

class MeetingRequest(BaseModel):
    transcript: str = Field(
        ...,
        min_length=10,
        description="The complete meeting transcript to analyze"
    )


# -----------------------------
# DECISION
# -----------------------------

class Decision(BaseModel):
    decision: str
    context: Optional[str] = None


# -----------------------------
# TASK / ACTION ITEM
# -----------------------------

class Task(BaseModel):
    task: str
    owner: Optional[str] = None
    deadline: Optional[str] = None
    status: str = "pending"


# -----------------------------
# UNRESOLVED QUESTION
# -----------------------------

class UnresolvedQuestion(BaseModel):
    question: str
    context: Optional[str] = None


# -----------------------------
# FOLLOW-UP
# -----------------------------

class FollowUp(BaseModel):
    action: str
    owner: Optional[str] = None
    deadline: Optional[str] = None


# -----------------------------
# CONTRADICTION
# -----------------------------

class Contradiction(BaseModel):
    topic: str
    statement_1: str
    statement_2: str
    explanation: Optional[str] = None


# -----------------------------
# UNCLEAR INSTRUCTION
# -----------------------------

class UnclearInstruction(BaseModel):
    instruction: str
    reason: str


# -----------------------------
# COMPLETE AGENT RESULT
# -----------------------------

class MeetingAnalysis(BaseModel):
    decisions: List[Decision] = Field(default_factory=list)

    tasks: List[Task] = Field(default_factory=list)

    unresolved_questions: List[UnresolvedQuestion] = Field(
        default_factory=list
    )

    follow_ups: List[FollowUp] = Field(
        default_factory=list
    )

    contradictions: List[Contradiction] = Field(
        default_factory=list
    )

    unclear_instructions: List[UnclearInstruction] = Field(
        default_factory=list
    )


# -----------------------------
# FINAL API RESPONSE
# -----------------------------

class MeetingResponse(BaseModel):
    success: bool
    data: MeetingAnalysis
    summary: str