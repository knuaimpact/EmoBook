from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from story.story_model import Story
from story.story_scene_model import StoryScene


class StoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_stories(self, skip: int = 0, limit: int = 20) -> list[Story]:
        stmt = select(Story).order_by(Story.id.desc()).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def get_story_detail(self, story_id: int) -> Story | None:
        stmt = (
            select(Story)
            .where(Story.id == story_id)
            .options(selectinload(Story.scenes))
        )
        return self.db.scalar(stmt)

    def get_scene(self, scene_id: int) -> StoryScene | None:
        return self.db.get(StoryScene, scene_id)

    def list_scenes(self, story_id: int) -> list[StoryScene]:
        stmt = (
            select(StoryScene)
            .where(StoryScene.story_id == story_id)
            .order_by(StoryScene.scene_order)
        )
        return list(self.db.scalars(stmt).all())

    def get_scene_for_story(self, story_id: int, scene_id: int) -> StoryScene | None:
        stmt = select(StoryScene).where(
            StoryScene.story_id == story_id,
            StoryScene.id == scene_id,
        )
        return self.db.scalar(stmt)
