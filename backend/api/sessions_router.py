from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from story.session_schema import (
    ChoiceRequest,
    NextSceneRequest,
    SessionSceneRead,
    SessionStartRequest,
)
from common.dependencies import get_database
from story.story_engine import SessionService

router = APIRouter(tags=["sessions"])


@router.post("/stories/{story_id}/start", response_model=SessionSceneRead)
def start_session(
    story_id: int,
    payload: SessionStartRequest,
    db: Session = Depends(get_database),
) -> SessionSceneRead:
    return SessionService(db).start_session(
        story_id=story_id,
        user_id=payload.user_id,
        child_profile_id=payload.child_profile_id,
    )


@router.get("/sessions/{session_id}/current-scene", response_model=SessionSceneRead)
def get_current_scene(
    session_id: int,
    db: Session = Depends(get_database),
) -> SessionSceneRead:
    return SessionService(db).get_current_scene(session_id=session_id)


@router.post("/sessions/{session_id}/next", response_model=SessionSceneRead)
def next_scene(
    session_id: int,
    payload: NextSceneRequest,
    db: Session = Depends(get_database),
) -> SessionSceneRead:
    return SessionService(db).next_scene(
        session_id=session_id,
        current_scene_id=payload.current_scene_id,
    )


@router.post("/sessions/{session_id}/choices", response_model=SessionSceneRead)
def make_choice(
    session_id: int,
    payload: ChoiceRequest,
    db: Session = Depends(get_database),
) -> SessionSceneRead:
    return SessionService(db).make_choice(
        session_id=session_id,
        choice_id=payload.choice_id,
    )
