from typing import List, Optional, Literal

from pydantic import BaseModel, Field


# =========================
# CHAT MESSAGE
# =========================

class ChatMessage(BaseModel):
    role: Literal[
        "user",
        "assistant"
    ]

    content: str


# =========================
# SOURCE / CITATION
# =========================

class KnowledgeSource(BaseModel):
    document: str = Field(
        ...,
        description="Name of the knowledge-base document"
    )

    section: Optional[str] = Field(
        default=None,
        description="Section or heading where the information was found"
    )


# =========================
# REQUEST SCHEMA
# =========================

class KnowledgeBaseRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=2,
        description="Employee or customer question"
    )

    conversation_history: List[ChatMessage] = Field(
        default_factory=list,
        description="Previous conversation messages used for follow-up context"
    )


# =========================
# RESPONSE DATA
# =========================

class KnowledgeBaseData(BaseModel):

    answer: str = Field(
        ...,
        description="Answer based only on the provided knowledge base"
    )

    sources: List[KnowledgeSource] = Field(
        default_factory=list,
        description="Knowledge-base sources supporting the answer"
    )

    status: Literal[
        "answered",
        "insufficient_information",
        "escalate"
    ] = Field(
        ...,
        description="Whether the question could be answered from the knowledge base"
    )

    context_used: bool = Field(
        default=False,
        description="Whether previous conversation context was used"
    )


# =========================
# FINAL API RESPONSE
# =========================

class KnowledgeBaseResponse(BaseModel):

    success: bool

    summary: str

    data: KnowledgeBaseData