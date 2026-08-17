# PharmaSentry — Secure Pharmacovigilance & Adverse Event Intelligence

**PharmaSentry** is an enterprise-grade AI-powered pharmacovigilance and adverse event intake platform. Built with **FastAPI**, **SQLAlchemy**, **AWS Bedrock AgentCore Runtime**, and **Strands Agents**, PharmaSentry provides automated PII redaction, structured adverse-event extraction, multi-tenant triage case management, openFDA drug label lookups, and clinical safety guardrails.

---

## Key Features

- **Secure Authentication & Session Management**:
  - JWT bearer token authentication with access tokens (30-minute expiry) and refresh tokens (7-day expiry).
  - Password hashing using `bcrypt`.
- **Automated Adverse Event Intake**:
  - Direct PII redaction (sanitizes patient names, DOBs, emails, phone numbers, and SSNs).
  - Structured extraction of patient age, gender, suspect drug, adverse events, and seriousness.
  - Automated inclusion of statistical signal caveats (*Signal ≠ Causality*).
- **Multi-Tenant Triage Queue**:
  - Isolated case storage with PostgreSQL backend.
  - Granular multi-tenant user access control (`/cases`, `/cases/{id}`).
- **AWS Bedrock AgentCore Streaming Integration**:
  - Real-time Server-Sent Events (SSE) streaming chat (`/chat`).
  - SigV4 request signing using AWS Bedrock credentials.
  - openFDA approved label lookup, drug safety statistics, and clinical trials search.
- **Clinical Guardrails & Human Escalation**:
  - Mandatory refusal policy for personalized clinical dosing advice.
  - Automatic escalation to human medical experts for diagnosis or dosing changes.

---

## Project Architecture

```
PharmaSentry/
├── backend/
│   └── app/
│       ├── core/                # Core settings, database connection, security
│       │   ├── config.py        # Centralized Pydantic settings & env configurations
│       │   ├── database.py      # SQLAlchemy engine, SessionLocal, get_db dependency
│       │   ├── security.py      # JWT creation/verification & bcrypt hashing
│       │   └── sigv4.py         # AWS SigV4 authentication handler for httpx
│       ├── models/              # SQLAlchemy ORM Database Models
│       │   ├── user.py          # DBUser model
│       │   ├── session.py       # DBSession model
│       │   ├── triage.py        # DBTriageCase model
│       │   └── drug_label.py    # DBDrugLabel model
│       ├── schemas/             # Pydantic Schemas & DTOs
│       │   ├── auth.py          # Signup, Login, TokenResponse, RefreshRequest
│       │   ├── chat.py          # ChatRequest
│       │   └── triage.py        # IntakeRequest, CaseResponse, TriageCaseExtraction
│       ├── services/            # Core Business Services
│       │   ├── pii_service.py   # Regex PII redaction service
│       │   └── agent_service.py # AWS AgentCore streaming & SigV4 auth
│       ├── routes/              # FastAPI Router Modules
│       │   ├── auth.py          # /auth/signup, /auth/login, /auth/refresh
│       │   ├── chat.py          # /chat endpoint
│       │   ├── intake.py        # /intake adverse event parsing endpoint
│       │   └── cases.py         # /cases queue endpoints
│       └── main.py              # FastAPI Application assembly & CORS setup
├── pharmasentry-agent/          # AWS AgentCore & Strands Agent implementation
│   ├── agentcore/               # AgentCore CDK infrastructure deployment
│   └── app/PharmaSentryAgent/   # Strands Agent application logic & tools
├── tests/                       # Verification & Test Suites
│   ├── test_system.py           # Integration test suite for all backend endpoints
│   ├── test_manual.py           # Benchmark test runner
│   ├── run_behavior_suite.py    # Behavioral evaluation suite
│   └── test_prompts.txt         # Evaluation prompts dataset
├── main.py                      # Root entrypoint redirecting to backend.app.main:app
└── README.md                    # Project Documentation
```

---

## Configuration & Environment Variables

Key configuration variables can be customized via environment variables:

| Environment Variable | Description | Example / Default |
| :--- | :--- | :--- |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://<username>:<password>@127.0.0.1:5432/pharmapp` |
| `JWT_SECRET` | Secret key used for signing JWT tokens | `<your-secure-jwt-secret-key>` |
| `AWS_REGION` | AWS Region for Bedrock AgentCore | `us-east-1` (or `ap-south-1`) |
| `AGENTCORE_RUNTIME_URL` | Optional override for AgentCore Runtime URL | *Auto-detected / AWS Deployed URL* |


---

## Installation & Setup

### 1. Prerequisites
- **Python**: 3.12+
- **PostgreSQL Database**: Running locally or remotely with a database named `pharmapp`.
- **AWS CLI**: Configured with valid SSO access (`aws sso login`).

### 2. Environment Activation & Dependencies
Activate the virtual environment and install requirements:

```powershell
# Activate Virtual Environment (Windows PowerShell)
.\venv\Scripts\activate

# Upgrade pip and install dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose bcrypt httpx boto3 pydantic pydantic-settings
```

### 3. AWS Authentication
Sign in to AWS SSO to enable SigV4 streaming invocation to the AWS Bedrock AgentCore Runtime:

```powershell
aws sso login
```

---

## Running the Server

Start the FastAPI application from the project root:

```powershell
python main.py
```

*Alternatively, run directly via Uvicorn:*

```powershell
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

The interactive API documentation (Swagger UI) will be accessible at:
- **Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## API Reference Overview

### 1. Authentication Endpoints
- `POST /auth/signup`: Register a new practitioner account.
- `POST /auth/login`: Authenticate and receive `access_token` and `refresh_token`.
- `POST /auth/refresh`: Exchange a valid refresh token for a new access token.

### 2. Adverse Event Intake & Triage
- `POST /intake`: Accepts a free-text patient adverse event narrative, redacts PII, parses structured details, inserts causality caveats, and saves to PostgreSQL.
- `GET /cases`: List all adverse event cases submitted by the authenticated user.
- `GET /cases/{case_id}`: Retrieve full details of a specific triage case.

### 3. Agent Streaming Chat
- `POST /chat`: Stream responses from the Bedrock AgentCore Runtime over Server-Sent Events (`text/event-stream`).

---

## Running Automated Verification Tests

To verify that all endpoints (Signup, Login, Token Refresh, Adverse Event Intake with PII Redaction, Cases Queue, and Agent Chat) are operating cleanly, run the system integration test suite:

```powershell
python tests/test_system.py
```
