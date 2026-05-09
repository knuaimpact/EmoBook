from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.schema.story import StoryDetail, StoryListItem, StorySceneRead
from app.service.dependencies import get_database
from app.service.story_service import StoryService

router = APIRouter(prefix="/stories", tags=["stories"])


@router.get("", response_model=list[StoryListItem])
def list_stories(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_database),
) -> list[StoryListItem]:
    return StoryService(db).list_stories(skip=skip, limit=limit)


@router.get("/{story_id}", response_model=StoryDetail)
def get_story_detail(
    story_id: int,
    db: Session = Depends(get_database),
) -> StoryDetail:
    return StoryService(db).get_story_detail(story_id)


@router.get("/{story_id}/scenes", response_model=list[StorySceneRead])
def list_story_scenes(
    story_id: int,
    db: Session = Depends(get_database),
) -> list[StorySceneRead]:
    return StoryService(db).list_scenes(story_id)


@router.get("/{story_id}/scenes/{scene_id}", response_model=StorySceneRead)
def get_story_scene(
    story_id: int,
    scene_id: int,
    db: Session = Depends(get_database),
) -> StorySceneRead:
    return StoryService(db).get_scene(story_id, scene_id)
