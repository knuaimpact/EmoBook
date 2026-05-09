from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.model.story import Story
from app.model.story_scene import StoryScene
from app.repository.story_repository import StoryRepository


class StoryService:
    def __init__(self, db: Session):
        self.story_repository = StoryRepository(db)

    def list_stories(self, *, skip: int = 0, limit: int = 20) -> list[Story]:
        return self.story_repository.list_stories(skip=skip, limit=limit)

    def get_story_detail(self, story_id: int) -> Story:
        story = self.story_repository.get_story_detail(story_id)
        if story is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Story not found",
            )
        return story

    def list_scenes(self, story_id: int) -> list[StoryScene]:
        story = self.story_repository.get_story_detail(story_id)
        if story is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Story not found",
            )
        return self.story_repository.list_scenes(story_id)

    def get_scene(self, story_id: int, scene_id: int) -> StoryScene:
        scene = self.story_repository.get_scene_for_story(story_id, scene_id)
        if scene is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Story scene not found",
            )
        return scene
