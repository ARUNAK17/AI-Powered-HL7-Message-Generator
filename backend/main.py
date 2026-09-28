from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(
    title="AI-Powered HL7 Message Generator",
    version="1.0.0",
    description="Generate and validate HL7 v2 ADT and ORU messages using the OpenAI API.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MessageType = Literal["ADT^A01", "ORU^R01"]


class PatientInput(BaseModel):
    message_type: MessageType = "ADT^A01"
    patient_id: str = Field(..., min_length=1, max_length=50)
    patient_name: str = Field(..., min_length=1, max_length=150)
    date_of_birth: str = Field(..., min_length=8, max_length=20)
    sex: str = Field(..., min_length=1, max_length=10)
    admission_date: str = Field(..., min_length=8, max_length=30)
    hospital: str = Field(..., min_length=1, max_length=150)
    doctor: str = Field(..., min_length=1, max_length=150)
    diagnosis: str = Field(..., min_length=1, max_length=300)
    observation: str | None = Field(default=None, max_length=500)


class ValidationResult(BaseModel):
    valid: bool
    message_type: str | None = None
    errors: List[str] = []
    warnings: List[str] = []
    segments: List[Dict[str, Any]] = []


class GenerateResponse(BaseModel):
    hl7_message: str
    validation: ValidationResult


def clean_model_output(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:hl7|text)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


def parse_hl7(message: str) -> List[str]:
    return [line.strip() for line in message.split("\n") if line.strip()]


def validate_hl7(message: str) -> ValidationResult:
    errors: List[str] = []
    warnings: List[str] = []
    segment_details: List[Dict[str, Any]] = []

    segments = parse_hl7(message)

    if not segments:
        return ValidationResult(valid=False, errors=["HL7 message is empty."])

    if not segments[0].startswith("MSH|"):
        errors.append("Message must start with an MSH segment.")

    for index, segment in enumerate(segments, start=1):
        fields = segment.split("|")
        segment_name = fields[0]
        segment_details.append(
            {
                "line": index,
                "segment": segment_name,
                "field_count": max(len(fields) - 1, 0),
            }
        )

    msh = segments[0].split("|") if segments[0].startswith("MSH|") else []
    message_type = None

    if len(msh) > 8:
        message_type = msh[8]
    else:
        errors.append("MSH-9 (Message Type) is missing.")

    if message_type and message_type not in {"ADT^A01", "ORU^R01"}:
        warnings.append(
            f"Message type '{message_type}' is not one of the supported UI types: ADT^A01 or ORU^R01."
        )

    names = [s.split("|", 1)[0] for s in segments]

    if "PID" not in names:
        errors.append("PID segment is required.")

    if message_type == "ADT^A01":
        if "EVN" not in names:
            errors.append("ADT^A01 requires an EVN segment.")
        if "PV1" not in names:
            warnings.append("ADT^A01 normally includes PV1 encounter information.")

    if message_type == "ORU^R01":
        if "OBR" not in names:
            errors.append("ORU^R01 requires an OBR segment.")
        if "OBX" not in names:
            errors.append("ORU^R01 requires at least one OBX observation segment.")

    for segment in segments:
        fields = segment.split("|")
        name = fields[0]

        if name == "PID" and len(fields) < 6:
            errors.append("PID segment does not contain the expected patient name fields.")

        if name == "MSH" and len(fields) < 12:
            errors.append("MSH segment is missing expected message metadata fields.")

    return ValidationResult(
        valid=len(errors) == 0,
        message_type=message_type,
        errors=errors,
        warnings=warnings,
        segments=segment_details,
    )


def build_prompt(data: PatientInput) -> str:
    observation = data.observation or "No additional observation supplied."

    return f"""
You are an HL7 v2 integration specialist.

Generate ONE syntactically structured HL7 v2 message for the requested event.

Requested message type: {data.message_type}

Patient:
- Patient ID: {data.patient_id}
- Patient name: {data.patient_name}
- Date of birth: {data.date_of_birth}
- Sex: {data.sex}
- Admission date/time: {data.admission_date}
- Hospital: {data.hospital}
- Doctor: {data.doctor}
- Diagnosis: {data.diagnosis}
- Observation: {observation}

Rules:
1. Return ONLY the HL7 message. Do not return Markdown, explanations, comments, or code fences.
2. Use pipe-delimited HL7 v2 segments and standard HL7 field separators.
3. Start with MSH.
4. For ADT^A01 include MSH, EVN, PID and PV1.
5. For ORU^R01 include MSH, PID, OBR and at least one OBX.
6. Use realistic but clearly fictional identifiers and timestamps where needed.
7. Keep the supplied patient values consistent across the message.
8. Do not invent sensitive clinical details beyond the supplied diagnosis/observation.
9. Make the message suitable for demonstration and development testing, not real clinical use.
""".strip()


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/validate", response_model=ValidationResult)
def validate(message: Dict[str, str]) -> ValidationResult:
    hl7_message = message.get("hl7_message", "")
    if not hl7_message.strip():
        raise HTTPException(status_code=400, detail="hl7_message is required.")
    return validate_hl7(hl7_message)


@app.post("/api/generate", response_model=GenerateResponse)
def generate(data: PatientInput) -> GenerateResponse:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is not configured. Copy .env.example to .env and add your key.",
        )

    try:
        client = OpenAI(api_key=api_key)

        response = client.responses.create(
            model=model,
            input=build_prompt(data),
        )

        hl7_message = clean_model_output(response.output_text)
        validation = validate_hl7(hl7_message)

        return GenerateResponse(
            hl7_message=hl7_message,
            validation=validation,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"OpenAI request failed: {str(exc)}",
        ) from exc
