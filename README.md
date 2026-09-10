# AI Agent Suite

A modular, multi-agent AI workspace that combines five specialized agents behind a single React + FastAPI application.

The application is designed around a simple principle: **each agent has a clearly defined responsibility, receives only the information required for that responsibility, and returns structured output that the frontend can render consistently.**

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Repository Structure](#repository-structure)
- [Application Flow](#application-flow)
- [Agent Architecture](#agent-architecture)
  - [1. AI Meeting Agent](#1-ai-meeting-agent)
  - [2. AI Competitor Watch Agent](#2-ai-competitor-watch-agent)
  - [3. AI Website QA Agent](#3-ai-website-qa-agent)
  - [4. AI Lead Qualification Agent](#4-ai-lead-qualification-agent)
  - [5. AI Knowledge-Base Support Agent](#5-ai-knowledge-base-support-agent)
- [LLM Integration](#llm-integration)
- [Data Validation](#data-validation)
- [API Reference](#api-reference)
- [Frontend Architecture](#frontend-architecture)
- [Knowledge Base and Retrieval](#knowledge-base-and-retrieval)
- [External Data Sources](#external-data-sources)
- [Error Handling and Fallbacks](#error-handling-and-fallbacks)
- [Configuration](#configuration)
- [Installation and Local Setup](#installation-and-local-setup)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Design and Engineering Decisions](#design-and-engineering-decisions)
- [Current Limitations](#current-limitations)
- [Future Improvements](#future-improvements)

---

## Overview

The AI Agent Suite is a single web application containing five independent AI workflows:

| # | Agent | Primary Function | Main Input |
|---|---|---|---|
| 1 | AI Meeting Agent | Converts meeting transcripts into structured action intelligence | Meeting transcript |
| 2 | AI Competitor Watch Agent | Finds and summarizes meaningful recent competitor updates | Company names |
| 3 | AI Website QA Agent | Inspects websites for technical, SEO, content and usability issues | Website URL |
| 4 | AI Lead Qualification Agent | Researches and ranks leads against an Ideal Customer Profile | CSV + ICP |
| 5 | AI Knowledge-Base Support Agent | Answers questions from a controlled company knowledge base | Question + optional conversation history |

The five agents are not implemented as one large prompt. Each agent has its own Python class, schema, prompt strategy, supporting services and API endpoint.

---

# Architecture

The application follows a **frontend → API → agent → service/data source → LLM → validation → frontend** pattern.

```text
                        ┌──────────────────────────┐
                        │       React Frontend     │
                        │   Vite + TypeScript      │
                        └────────────┬─────────────┘
                                     │ HTTP / JSON
                                     ▼
                        ┌──────────────────────────┐
                        │       FastAPI API         │
                        │        app/main.py        │
                        └────────────┬─────────────┘
                                     │
               ┌─────────────────────┼─────────────────────┐
               │                     │                     │
               ▼                     ▼                     ▼
        Meeting Agent        Competitor Agent       Website QA Agent
               │                     │                     │
               │                     ▼                     ▼
               │              Google News RSS      Website QA Service
               │                     │                     │
               └──────────────┬──────┴──────────────┬──────┘
                              │                     │
                              ▼                     ▼
                       OpenAI-compatible       Website content
                         LLM service             + checks
                              │
                              ▼
                       Structured response

               ┌─────────────────────┴─────────────────────┐
               │                                           │
               ▼                                           ▼
      Lead Qualification Agent                  Knowledge Base Agent
               │                                           │
               ▼                                           ▼
      Lead Research Service                    Local Markdown KB
               │                                           │
               ├── Google Search                        Retrieval
               └── Company website                         │
                       │                                    ▼
                       └───────────────► LLM ◄──────────────┘
```

### Architectural layers

**Presentation layer**
- React
- TypeScript
- Vite
- Agent-specific UI components

**API layer**
- FastAPI
- HTTP endpoints
- Request/response validation
- CORS configuration

**Agent layer**
- `MeetingAgent`
- `CompetitorAgent`
- `WebsiteQAAgent`
- `LeadQualificationAgent`
- `KnowledgeBaseAgent`

**Service layer**
- `LLMService`
- `SearchService`
- `WebsiteQAService`
- `LeadResearchService`
- `KnowledgeBaseService`

**Schema layer**
- Pydantic models defining API contracts and agent output structures

**Data layer**
- Markdown knowledge-base documents
- Uploaded CSV lead data
- Runtime website/news research

---

# Technology Stack

## Frontend

- React 19
- TypeScript
- Vite
- CSS
- React state management using `useState`
- Native `fetch()` for API communication

## Backend

- Python
- FastAPI
- Pydantic
- Uvicorn
- `python-dotenv`
- OpenAI-compatible client

## AI / LLM

The project uses an OpenAI-compatible API interface.

Configuration is supplied through:

```env
LLM_API_KEY=your_api_key
LLM_BASE_URL=your_base_url
LLM_MODEL=your_model
```

The application does not hard-code the model provider inside individual agents. Every agent calls the common `LLMService`.

## Web / Data Processing

- `requests`
- `BeautifulSoup4`
- `feedparser`
- Python CSV parsing
- `urllib.parse`

---

# Repository Structure

```text
project-root/
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── meeting_agent.py
│   │   │   ├── competitor_agent.py
│   │   │   ├── website_qa_agent.py
│   │   │   ├── lead_qualification_agent.py
│   │   │   └── knowledge_base_agent.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── meeting.py
│   │   │   ├── competitor.py
│   │   │   ├── website_qa.py
│   │   │   ├── lead_qualification.py
│   │   │   └── knowledge_base.py
│   │   │
│   │   ├── services/
│   │   │   ├── llm_service.py
│   │   │   ├── search_service.py
│   │   │   ├── website_qa_service.py
│   │   │   ├── lead_research_service.py
│   │   │   └── knowledge_base_service.py
│   │   │
│   │   └── main.py
│   │
│   ├── knowledge_base/
│   │   ├── benefits_and_payroll.md
│   │   ├── company_overview.md
│   │   ├── customer_support.md
│   │   ├── expense_policy.md
│   │   ├── hr_policies.md
│   │   ├── it_support.md
│   │   ├── leave_and_attendance.md
│   │   ├── remote_work.md
│   │   ├── security_policy.md
│   │   └── README.md
│   │
│   ├── requirements.txt
│   └── ...
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── MeetingAgent.tsx
    │   │   ├── CompetitorAgent.tsx
    │   │   ├── WebsiteQAAgent.tsx
    │   │   ├── LeadQualificationAgent.tsx
    │   │   └── KnowledgeBaseAgent.tsx
    │   │
    │   ├── data/
    │   │   ├── sampleTranscript.ts
    │   │   └── sampleLeads.ts
    │   │
    │   ├── App.tsx
    │   ├── main.tsx
    │   └── ...
    │
    ├── package.json
    └── vite.config.ts
```

> `node_modules`, Python virtual environments, caches and generated files should not be committed to GitHub.

---

# Application Flow

A typical request follows these steps:

```text
1. User selects an agent
        ↓
2. Frontend collects input
        ↓
3. React sends HTTP request
        ↓
4. FastAPI validates request
        ↓
5. Correct Agent class is invoked
        ↓
6. Agent obtains additional data if required
        ↓
7. Agent constructs controlled LLM prompt
        ↓
8. Common LLMService sends request
        ↓
9. LLM returns structured JSON/text
        ↓
10. Agent parses and validates response
        ↓
11. Backend returns Pydantic response
        ↓
12. React renders result
```

This separation prevents UI code from containing the business logic of the agents.

---

# Agent Architecture

## 1. AI Meeting Agent

### Purpose

Transforms an unstructured meeting transcript into structured, actionable intelligence.

### Input

```json
{
  "transcript": "Complete meeting transcript..."
}
```

### Processing

```text
Transcript
   ↓
MeetingAgent
   ↓
Controlled LLM prompt
   ↓
JSON parsing
   ↓
Pydantic validation
   ↓
Deterministic summary
   ↓
MeetingResponse
```

### The agent extracts

- Confirmed decisions
- Tasks/action items
- Task owners
- Deadlines
- Unresolved questions
- Follow-ups
- Contradictions
- Unclear instructions

### Important reasoning rules

The prompt explicitly prevents common hallucination errors.

For example:

- A speaker giving an instruction is not automatically assumed to own the task.
- A deadline is only recorded when explicitly stated.
- Suggestions are not treated as decisions unless agreement is clear.
- Actionable instructions remain tasks even when the owner is unknown.
- Follow-ups are reserved for future checks, discussions, meetings or actions.
- Contradictions must represent genuine conflicts.
- Unclear instructions are only reported when clarification is actually needed.

### Output model

```json
{
  "decisions": [],
  "tasks": [],
  "unresolved_questions": [],
  "follow_ups": [],
  "contradictions": [],
  "unclear_instructions": []
}
```

The application generates the final summary from the validated result rather than asking the LLM to generate the summary.

### Endpoint

```http
POST /api/meeting/analyze
```

---

# 2. AI Competitor Watch Agent

## Purpose

Monitors named competitors and converts recent news into concise competitive intelligence.

### Input

```json
{
  "companies": [
    "OpenAI",
    "Anthropic",
    "Google"
  ]
}
```

Maximum configured companies: 10.

### Data collection

The `SearchService` queries Google News RSS and collects recent entries.

Each raw result contains:

```text
title
link
published
summary
```

The current agent sends a reduced set of fields to the LLM:

```text
title
link
published
```

### Processing pipeline

```text
Company names
     ↓
Google News RSS
     ↓
Raw results
     ↓
Cleaned results
     ↓
LLM
     ↓
Remove noise / duplicates
     ↓
Categorize updates
     ↓
CompetitorResponse
```

### Supported update categories

- `product`
- `pricing`
- `hiring`
- `partnership`
- `funding`
- `acquisition`
- `leadership`
- `other`

### Prompt strategy

The LLM is instructed to:

1. Use only supplied search results.
2. Remove irrelevant news.
3. Remove duplicate or near-duplicate updates.
4. Categorize meaningful updates.
5. Preserve exact source URLs.
6. Avoid invented dates.
7. Avoid fabricated facts.
8. Explain why each update matters.
9. Include every requested company even if it has no meaningful update.

### Output

```json
{
  "companies": [
    {
      "company": "Company name",
      "updates": [
        {
          "title": "...",
          "category": "product",
          "summary": "...",
          "why_it_matters": "...",
          "source": "...",
          "date": "..."
        }
      ]
    }
  ],
  "intelligence_brief": "..."
}
```

### Endpoint

```http
POST /api/competitor/analyze
```

---

# 3. AI Website QA Agent

## Purpose

Combines deterministic website inspection with LLM-based qualitative analysis.

This agent is deliberately split into two stages:

```text
Deterministic inspection → Confirmed issues
LLM analysis              → Suspected issues
```

This distinction is important because a website crawler can verify some technical problems, while UI/content quality often requires interpretation.

## URL normalization

The service accepts:

```text
example.com
www.example.com
http://example.com
https://example.com
```

If no scheme is supplied, the service adds:

```text
https://
```

### Deterministic checks

The `WebsiteQAService` currently checks:

- HTTP response status
- Page title
- Meta description
- H1 count
- Image sources
- Broken/unreachable images
- Links
- Broken/unreachable HTTP/HTTPS links
- Extracted page text

### Limits

- Website request timeout: 10 seconds
- Maximum links checked: 30
- Maximum images checked: 20
- Extracted page text sent to the LLM: up to 8,000 characters

### Confirmed issue examples

```text
Missing page title
Missing meta description
No H1 heading
Broken link
Image could not be loaded
Website returned HTTP error
```

These are generated from actual programmatic checks.

### LLM stage

The LLM receives:

- Website URL
- Extracted website text
- Confirmed issues
- SEO data

It is instructed to identify only potential:

- UI issues
- Content issues
- Usability issues
- SEO observations

The LLM must place uncertain observations in `suspected_issues` and must not present them as confirmed technical failures.

### Output

```json
{
  "success": true,
  "url": "...",
  "summary": "...",
  "data": {
    "confirmed_issues": [],
    "suspected_issues": [],
    "seo_report": {
      "title": "...",
      "meta_description": "...",
      "h1_count": 1
    },
    "priority_actions": []
  }
}
```

### Endpoint

```http
POST /api/website-qa/analyze
```

---

# 4. AI Lead Qualification Agent

## Purpose

Researches leads and evaluates them against a user-defined Ideal Customer Profile (ICP).

This is the most multi-stage agent in the application.

## Input

The frontend sends:

- CSV file
- ICP configuration

The ICP can contain:

```text
target industries
minimum company size
maximum company size
target locations
required technologies
target business models
additional criteria
```

### Processing pipeline

```text
CSV upload
    ↓
CSV parsing
    ↓
Lead records
    ↓
Company research
    ├── Google search
    └── Optional supplied website
    ↓
Research evidence
    ↓
LLM criterion evaluation
    ↓
match / partial / not_match / unknown
    ↓
Python deterministic score
    ↓
Fit category
    ↓
Ranking
    ↓
Top 5 prospects
```

### Lead research

`LeadResearchService`:

1. Searches Google for the company.
2. Collects up to five search results.
3. Records source links.
4. If a website is supplied, fetches the website.
5. Extracts title, description and up to 8,000 characters of text.

### Evidence rules

The LLM is explicitly told:

- Never invent missing information.
- Unknown information must remain `unknown`.
- Search-result titles alone should not be treated as confirmed facts.
- Each ICP dimension is evaluated once.
- Company size is one criterion, not separate minimum/maximum criteria.
- Multiple acceptable industries/locations/technologies are evaluated as a whole.

### Qualification statuses

| Status | Meaning |
|---|---|
| `match` | Evidence supports the criterion |
| `partial` | Some but not all relevant evidence supports the criterion |
| `not_match` | Evidence indicates the criterion is not satisfied |
| `unknown` | There is not enough verified evidence |

### Deterministic scoring

The LLM does **not** calculate the final score.

The Python application calculates it:

```text
match       = 1.0
partial     = 0.5
not_match   = 0
unknown     = 0
```

Every returned criterion has equal weight.

```text
score = (total criterion points / number of criteria) × 100
```

The result is rounded to an integer.

### Fit normalization

```text
80–100 → high
60–79  → medium
0–59   → low
```

### Qualification threshold

A lead is counted as "qualified" when:

```text
score >= 70
```

This is intentionally separate from the `fit` labels.

### Ranking

All leads are sorted by score in descending order.

The first five are exposed as:

```text
top_prospects
```

### Endpoint

```http
POST /api/lead-qualification/analyze
```

This endpoint uses `multipart/form-data` because it receives both a CSV file and serialized ICP JSON.

---

# 5. AI Knowledge-Base Support Agent

## Purpose

Provides controlled question answering over the local NotRealOrg knowledge base.

Unlike an unrestricted chatbot, this agent is designed to answer only from supplied organizational documents.

## Knowledge sources

The knowledge base currently contains Markdown documents covering areas such as:

- Company overview
- Benefits and payroll
- Customer support
- Expense policy
- HR policies
- IT support
- Leave and attendance
- Remote work
- Security policy

`README.md` inside the knowledge-base directory is ignored as documentation rather than answerable knowledge.

## Retrieval pipeline

```text
User question
     ↓
Optional recent conversation context
     ↓
Tokenization
     ↓
Keyword overlap retrieval
     ↓
Relevance scoring
     ↓
Top 5 sections
     ↓
LLM receives retrieved context
     ↓
Answer + source validation
     ↓
KnowledgeBaseResponse
```

### Retrieval algorithm

This implementation uses lightweight lexical retrieval rather than embeddings/vector search.

For each Markdown section:

1. Tokenize the query.
2. Tokenize the section heading and content.
3. Remove common stop words.
4. Find overlapping meaningful words.
5. Require at least two matching words.
6. Base score = number of matching words.
7. Heading matches receive additional weight.
8. Exact question phrase receives a boost.
9. Results are sorted by score.
10. Top five sections are returned.

### Why this is useful

It keeps the knowledge-base implementation:

- lightweight
- easy to inspect
- deterministic
- dependency-light
- easy to replace with vector retrieval later

### Conversation history

The agent supports follow-up questions.

Recent conversation messages are used to improve retrieval context and understand references such as:

```text
User: How many annual leave days do employees get?
AI: 18 days...
User: Can I carry them forward?
```

The conversation history is **not** treated as an independent source of organizational facts. The knowledge-base documents remain the factual source.

### Hallucination controls

The prompt requires:

- no outside knowledge
- no guessing
- no invented policies
- exact preservation of numbers, dates and limits
- only valid knowledge-base document/section citations
- `insufficient_information` when evidence is unavailable

After the LLM responds, the backend verifies that every cited source actually exists among the retrieved sections.

If an `answered` response contains no valid source, it is downgraded to:

```text
insufficient_information
```

### Status values

```text
answered
insufficient_information
escalate
```

### Endpoint

```http
POST /api/knowledge-base/answer
```

---

# LLM Integration

All agents use the same `LLMService`.

## `LLMService`

The service reads:

```env
LLM_API_KEY
LLM_BASE_URL
LLM_MODEL
```

and creates an OpenAI-compatible client:

```python
OpenAI(
    api_key=self.api_key,
    base_url=self.base_url
)
```

Agents therefore remain provider-independent.

They call:

```python
self.llm_service.chat(
    messages=messages,
    temperature=...
)
```

rather than constructing an API client themselves.

## Temperature choices

The agents use low temperatures because the application is primarily performing structured analysis rather than creative generation.

Typical configuration:

```text
Meeting Agent:          0.1
Competitor Agent:       0.1
Website QA Agent:       0.1
Lead Qualification:     0.1
Knowledge Base:         0.0
```

The knowledge-base agent uses zero temperature to favor consistency.

---

# Data Validation

Pydantic schemas define the contracts between the API, agents and frontend.

Examples include:

```text
MeetingRequest
MeetingResponse
MeetingAnalysis

CompetitorRequest
CompetitorResponse
CompanyIntelligence
CompetitorUpdate

WebsiteQARequest
WebsiteQAResponse
WebsiteQAData
QAIssue
SEOReport

LeadQualificationRequest
LeadQualificationResponse
QualifiedLead
QualificationReason
ICP

KnowledgeBaseRequest
KnowledgeBaseResponse
KnowledgeBaseData
KnowledgeSource
ChatMessage
```

This gives the application explicit types for:

- required fields
- optional fields
- list structures
- literal status values
- score ranges
- request limits

---

# API Reference

## Health

### `GET /`

Returns:

```json
{
  "message": "AI Agent Suite Backend is running"
}
```

### `GET /health`

Returns:

```json
{
  "status": "healthy"
}
```

---

## Meeting

### `POST /api/meeting/analyze`

Request:

```json
{
  "transcript": "..."
}
```

Response:

```json
{
  "success": true,
  "data": {
    "decisions": [],
    "tasks": [],
    "unresolved_questions": [],
    "follow_ups": [],
    "contradictions": [],
    "unclear_instructions": []
  },
  "summary": "..."
}
```

---

## Competitor

### `POST /api/competitor/analyze`

Request:

```json
{
  "companies": ["OpenAI", "Anthropic", "Google"]
}
```

Response:

```json
{
  "companies": [],
  "intelligence_brief": "..."
}
```

---

## Website QA

### `POST /api/website-qa/analyze`

Request:

```json
{
  "url": "example.com"
}
```

Response contains:

```text
confirmed_issues
suspected_issues
seo_report
priority_actions
```

---

## Lead Qualification

### `POST /api/lead-qualification/analyze`

Content type:

```text
multipart/form-data
```

Fields:

```text
file = CSV file
icp  = JSON string
```

Example ICP:

```json
{
  "target_industries": ["SaaS", "Technology"],
  "company_size_min": 50,
  "company_size_max": 500,
  "target_locations": ["United States"],
  "required_technologies": ["Python"],
  "target_business_models": ["B2B"],
  "additional_criteria": ["Growing company"]
}
```

---

## Knowledge Base

### `POST /api/knowledge-base/answer`

Request:

```json
{
  "question": "How many annual leave days do employees get?",
  "conversation_history": []
}
```

Response:

```json
{
  "success": true,
  "summary": "...",
  "data": {
    "answer": "...",
    "sources": [],
    "status": "answered",
    "context_used": false
  }
}
```

---

# Frontend Architecture

The React application uses a central `App.tsx` as the workspace controller.

The application maintains:

```text
selectedAgent
initialTranscript
initialCompanies
initialWebsiteUrl
initialLeadCSV
initialLeadICP
```

Selecting an agent renders its dedicated component.

```text
App.tsx
 ├── MeetingAgent.tsx
 ├── CompetitorAgent.tsx
 ├── WebsiteQAAgent.tsx
 ├── LeadQualificationAgent.tsx
 └── KnowledgeBaseAgent.tsx
```

Each component is responsible for:

- local input state
- loading state
- error state
- API request
- response state
- rendering the result

The application also provides example/demo inputs from:

```text
src/data/sampleTranscript.ts
src/data/sampleLeads.ts
```

The left workspace sidebar allows example data to be loaded into the relevant agent.

---

# Knowledge Base and Retrieval

The knowledge base is intentionally filesystem-based.

At application startup:

```text
KnowledgeBaseService
        ↓
Locate backend/knowledge_base
        ↓
Read *.md
        ↓
Ignore README.md
        ↓
Split by "## " headings
        ↓
Store document + section + content
```

Each section becomes a retrievable unit.

This means the knowledge base can be extended simply by adding another Markdown document with appropriately structured `##` headings.

---

# External Data Sources

## Competitor Agent

Uses Google News RSS through:

```text
news.google.com/rss/search
```

The application retrieves current search-feed results at request time.

## Lead Qualification Agent

Uses Google search pages for company discovery and optionally fetches a supplied company website.

Because these sources are external, availability and page structure can affect results.

## Website QA Agent

Directly requests the submitted website and its detected links/images.

The agent does not use a browser engine; it performs HTTP requests and HTML parsing.

---

# Error Handling and Fallbacks

The application includes several defensive layers.

## API-level errors

FastAPI catches agent failures and converts them to HTTP errors.

## LLM failures

Agents handle cases such as:

- connection failures
- API errors
- rate limits
- empty responses
- invalid JSON

## JSON cleanup

Some agents remove Markdown code fences when the model returns:

```text
```json
{ ... }
```
```

## Deterministic fallbacks

The competitor and lead agents can return safe fallback structures when processing cannot be completed.

The lead qualification fallback marks criteria as `unknown` rather than assuming a match.

## Knowledge-base source validation

Knowledge-base citations are checked against actual retrieved sections before being accepted.

---

# Configuration

Create a `.env` file for the backend.

```env
LLM_API_KEY=your_api_key
LLM_BASE_URL=your_openai_compatible_base_url
LLM_MODEL=auto
```

Do not commit `.env`.

Recommended `.gitignore` entries:

```gitignore
.env
.venv/
venv/
__pycache__/
node_modules/
dist/
```

---

# Installation and Local Setup

## 1. Clone the repository

```bash
git clone <your-repository-url>
cd <your-repository>
```

## 2. Backend

Open a terminal in `backend`:

```bash
cd backend
```

Create a virtual environment:

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env`:

```env
LLM_API_KEY=...
LLM_BASE_URL=...
LLM_MODEL=...
```

## 3. Frontend

Open another terminal:

```bash
cd frontend
npm install
```

---

# Running the Application

## Start backend

From `backend`:

```bash
uvicorn app.main:app --reload --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

## Start frontend

From `frontend`:

```bash
npm run dev
```

Vite will display the local frontend URL, normally:

```text
http://localhost:5173
```

The current frontend components use:

```text
http://127.0.0.1:8000
```

as the backend base address.

---

# Testing

The backend contains basic service/connection test files:

```text
backend/test_connection.py
backend/test_llm_service.py
```

The frontend provides example data for manually testing:

- Meeting analysis
- Competitor monitoring
- Website QA
- Lead qualification

The Knowledge Base agent also provides suggested questions in the UI.

---

# Design and Engineering Decisions

## 1. One service for all LLM calls

Instead of duplicating API client configuration in every agent, `LLMService` centralizes it.

Benefits:

- provider independence
- simpler configuration
- easier model replacement
- less duplicated code

## 2. Agents are independent

Each agent has its own class.

This makes it possible to:

- modify one workflow without breaking another
- test agents independently
- add additional agents later
- maintain agent-specific prompts

## 3. LLM and deterministic logic are separated

Where possible, the application lets Python handle objective calculations.

For example, lead scoring is calculated by Python rather than trusting the model to calculate it.

Similarly, website technical checks are performed programmatically before the LLM provides qualitative analysis.

## 4. Structured outputs

The agents are instructed to return JSON, then the application validates the response.

This is safer than directly displaying arbitrary model output.

## 5. Evidence-first behavior

The prompts repeatedly instruct agents not to invent missing information.

This is especially important for:

- meeting ownership
- competitor intelligence
- lead qualification
- company policies
- website issues

## 6. Controlled knowledge-base answers

The Knowledge Base agent uses retrieval before generation and validates citations afterward.

This reduces the risk of an unrestricted model answering company-policy questions from general knowledge.

---

# Current Limitations

1. The frontend currently uses a hard-coded local backend URL.
2. Authentication and authorization are not implemented.
3. Rate limiting is not implemented at the application level.
4. Competitor research depends on external Google News RSS availability.
5. Lead research depends on external search/website accessibility.
6. Website QA is HTTP/HTML based and does not execute JavaScript-heavy pages.
7. Website QA does not perform full browser-based accessibility testing.
8. Knowledge-base retrieval is keyword-based rather than embedding/vector based.
9. Knowledge-base documents are local Markdown files rather than a database.
10. Long-running lead research is currently processed synchronously.
11. There is no persistent database for request history.
12. Production deployment requires replacing local CORS/backend configuration.
13. Search and website scraping behavior can change when external websites change their HTML structure.

---

# Future Improvements

Potential next-stage improvements include:

- Environment-based frontend API URLs
- Authentication and user accounts
- Persistent database
- Redis/background task processing
- Async research workers
- Vector database for semantic knowledge retrieval
- Embedding-based RAG
- Browser automation for JavaScript-rendered websites
- Lighthouse/PageSpeed integration
- More robust web search APIs
- Source confidence scoring
- Agent execution tracing
- Request history and saved reports
- Export reports to PDF/CSV
- Automated unit and integration test coverage
- Docker deployment
- CI/CD pipeline
- Production logging and monitoring

---

# Security Notes

Never commit:

```text
.env
LLM_API_KEY
private credentials
API tokens
```

External websites and search results should be treated as untrusted input.

The LLM is deliberately instructed not to treat missing information as verified information.

For production use, additional controls should be added for:

- authentication
- authorization
- rate limiting
- input size limits
- SSRF protection for arbitrary website URLs
- file upload validation
- logging and monitoring
- secret management

---

# Project Summary

The AI Agent Suite demonstrates a modular approach to building practical AI systems.

Rather than using one general chatbot for every task, the application separates responsibilities into five focused agents:

```text
Meeting Intelligence
        +
Competitor Intelligence
        +
Website Quality Analysis
        +
Lead Intelligence
        +
Knowledge-Base Support
        =
AI Agent Suite
```

The core engineering pattern is:

```text
Specialized Agent
      ↓
Controlled Input
      ↓
External/Local Evidence
      ↓
LLM Reasoning
      ↓
Structured Validation
      ↓
Reliable Application Output
```

This architecture makes the system easier to understand, extend, test and maintain than a single monolithic AI workflow.
