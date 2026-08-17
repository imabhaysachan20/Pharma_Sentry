import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.session import DBSession
from backend.app.schemas.chat import ChatRequest
from backend.app.services.agent_service import stream_agent

router = APIRouter(tags=["Chat"])

@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    correlation_id = str(uuid.uuid4())
    user_id = current_user["id"]

    # Retrieve or generate agent session
    if request.session_id:
        db_sess = db.query(DBSession).filter(
            DBSession.id == request.session_id,
            DBSession.user_id == user_id
        ).first()
        if not db_sess:
            raise HTTPException(status_code=404, detail="Session not found for this user.")
        agentcore_session_id = db_sess.agentcore_session_id
        session_id = request.session_id
    else:
        # Create a new session
        session_id = str(uuid.uuid4())
        agentcore_session_id = str(uuid.uuid4())
        new_sess = DBSession(id=session_id, user_id=user_id, agentcore_session_id=agentcore_session_id)
        db.add(new_sess)
        db.commit()

    return StreamingResponse(
        stream_agent(request.prompt, agentcore_session_id, correlation_id, user_id),
        media_type="text/event-stream"
    )
