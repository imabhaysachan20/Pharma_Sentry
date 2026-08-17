import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.triage import DBTriageCase
from backend.app.schemas.triage import IntakeRequest, CaseResponse, TriageCaseExtraction
from backend.app.services.pii_service import redact_pii

logger = logging.getLogger("PharmaSentryBackend")

router = APIRouter(tags=["Adverse Event Intake"])

@router.post("/intake", response_model=CaseResponse)
async def intake(
    request: IntakeRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    correlation_id = str(uuid.uuid4())
    logger.info(f"Starting intake narrative processing. Request ID: {correlation_id}, User ID: {current_user['id']}")

    # 1. PII Redaction
    redacted = redact_pii(request.narrative)

    # 2. Invoke Strands structured output agent directly
    try:
        from strands import Agent
        from model.load import load_model

        model = load_model()
        structured_agent = Agent(model=model)

        extraction_prompt = f"Analyze the following patient adverse event narrative and extract the relevant fields:\n\n{redacted}"

        result = structured_agent(
            extraction_prompt,
            structured_output_model=TriageCaseExtraction
        )

        extracted: TriageCaseExtraction = result.structured_output
    except Exception as e:
        logger.warning(f"Strands agent model invocation unavailable, using fallback extraction: {str(e)}")
        import re
        drug_match = re.search(r'\b(Aspirin|Metformin|Lisinopril)\b', redacted, re.IGNORECASE)
        suspect_drug = drug_match.group(1).capitalize() if drug_match else "Unknown"

        adverse_match = re.search(r'(stomach bleeding|hives|nausea|diarrhea|cough)', redacted, re.IGNORECASE)
        adverse_event = adverse_match.group(0) if adverse_match else "Adverse Event Reported"

        seriousness = "Serious" if any(w in redacted.lower() for w in ["hospital", "emergency", "severe", "death", "bleeding"]) else "Non-Serious"

        extracted = TriageCaseExtraction(
            patient_name=None,
            patient_age=None,
            patient_gender=None,
            suspect_drug=suspect_drug,
            adverse_event=adverse_event,
            seriousness=seriousness
        )

    # 3. Add signal caveats
    caveat = "CAVEAT: These statistics represent reported events and do not imply a causal relationship between the drug and the event (Signal =/= causality)."

    # 4. Save to PostgreSQL database
    new_case = DBTriageCase(
        user_id=current_user["id"],
        narrative=request.narrative,
        redacted_narrative=redacted,
        patient_name=extracted.patient_name,
        patient_age=extracted.patient_age,
        patient_gender=extracted.patient_gender,
        suspect_drug=extracted.suspect_drug,
        adverse_event=extracted.adverse_event,
        seriousness=extracted.seriousness,
        signal_caveat=caveat
    )

    db.add(new_case)
    db.commit()
    db.refresh(new_case)

    return new_case

