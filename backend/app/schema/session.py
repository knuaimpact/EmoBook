from pydantic import BaseModel, Field

from app.schema.common import Timestamped
from app.schema.story import StorySceneRead


class StoryChoiceRead(Timestamped):
    id: int
    scene_id: int
    choice_text: str
    next_scene_id: int | None = None
    action_type: str


class SessionStartRequest(BaseModel):
    child_profile_id: int
    voice_profile_id: int | None = None
    user_id: int  # Added temporarily until JWT is fully implemented to simulate logged-in user


class SessionSceneRead(BaseModel):
    session_id: int
    current_scene: StorySceneRead
    choices: list[StoryChoiceRead] = Field(default_factory=list)


class NextSceneRequest(BaseModel):
    current_scene_id: int


class ChoiceRequest(BaseModel):
    choice_id: int
