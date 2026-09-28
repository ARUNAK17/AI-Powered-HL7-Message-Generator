# AI-Powered HL7 Message Generator

A full-stack application that converts structured patient input into HL7 v2 messages using the OpenAI API and validates the generated message at segment level.

## Features

- Generate HL7 v2 `ADT^A01` messages
- Generate HL7 v2 `ORU^R01` messages
- OpenAI-powered message generation
- FastAPI backend
- Next.js frontend
- Segment-level HL7 validation
- Validation errors and warnings
- Segment summary table
- REST API architecture
- Docker-ready project structure
- No real patient data required

## Tech Stack

### Backend
- Python
- FastAPI
- OpenAI API
- Pydantic
- Uvicorn

### Frontend
- Next.js
- React
- TypeScript

## Architecture

```text
┌──────────────────────┐
│      Next.js UI      │
│  Patient Input Form  │
└──────────┬───────────┘
           │ HTTP
           ▼
┌──────────────────────┐
│     FastAPI API      │
│                      │
│  /api/generate       │
│  /api/validate       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│      OpenAI API      │
│  HL7 Message Create  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   HL7 Validator      │
│ MSH/PID/EVN/PV1/OBR  │
│        /OBX           │
└──────────────────────┘
```

## Project Structure

```text
ai-powered-hl7-message-generator/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── next.config.ts
│   ├── package.json
│   ├── tsconfig.json
│   └── .env.local.example
│
├── .gitignore
└── README.md
```

## Backend Setup

Open a terminal:

```bash
cd backend
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your environment file:

```bash
copy .env.example .env
```

or on macOS/Linux:

```bash
cp .env.example .env
```

Add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

Start the backend:

```bash
uvicorn main:app --reload --port 8000
```

Backend:

```text
http://localhost:8000
```

Swagger API documentation:

```text
http://localhost:8000/docs
```

## Frontend Setup

Open another terminal:

```bash
cd frontend
npm install
```

Create the local environment file.

Windows:

```bash
copy .env.local.example .env.local
```

macOS/Linux:

```bash
cp .env.local.example .env.local
```

The default value is:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start Next.js:

```bash
npm run dev
```

Open:

```text
http://localhost:3000
```

## API Endpoints

### Health Check

```http
GET /health
```

### Generate HL7

```http
POST /api/generate
```

Example request:

```json
{
  "message_type": "ADT^A01",
  "patient_id": "P10001",
  "patient_name": "DOE^JOHN",
  "date_of_birth": "19900115",
  "sex": "M",
  "admission_date": "20260928103000",
  "hospital": "Demo General Hospital",
  "doctor": "SMITH^JANE",
  "diagnosis": "Pneumonia",
  "observation": "Temperature 38.2 C"
}
```

### Validate HL7

```http
POST /api/validate
```

Example:

```json
{
  "hl7_message": "MSH|^~\\&|..."
}
```

## Example HL7 Flow

For an ADT admission:

```text
Patient Input
     ↓
OpenAI API
     ↓
MSH
EVN
PID
PV1
     ↓
Segment Validation
     ↓
Validation Result
```

For an ORU observation:

```text
Patient Input
     ↓
OpenAI API
     ↓
MSH
PID
OBR
OBX
     ↓
Segment Validation
     ↓
Validation Result
```

## Important

This application is intended for development, demonstration and educational purposes.

Do not enter real patient information or production clinical data into the application.

Generated HL7 messages should be validated against the requirements of the target healthcare system before any integration or production use.
