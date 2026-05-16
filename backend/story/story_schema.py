from pydantic import Field

from common.common_schema import Timestamped


class StorySceneRead(Timestamped):
    id: int
    story_id: int
    scene_order: int
    title: str | None = None
    text: str
    image_url: str | None = None


class StoryListItem(Timestamped):
    id: int
    title: str
    summary: str | None = None
    cover_image_url: str | None = None
    age_range: str | None = None


class StoryDetail(StoryListItem):
    scenes: list[StorySceneRead] = Field(default_factory=list)
