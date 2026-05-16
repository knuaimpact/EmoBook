from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.model.child_profile import ChildProfile
from app.model.story import Story
from app.model.story_choice import StoryChoice
from app.model.story_scene import StoryScene
from app.model.user_choice_log import UserChoiceLog
from app.model.user_story_session import UserStorySession
from app.schema.session import SessionSceneRead, StoryChoiceRead
from app.schema.story import StorySceneRead


class SessionService:
    def __init__(self, db: Session):
        self.db = db

    def start_session(
        self, story_id: int, user_id: int, child_profile_id: int
    ) -> SessionSceneRead:
        story = self.db.scalar(select(Story).where(Story.id == story_id))
        if not story:
            raise HTTPException(status_code=404, detail="Story not found")

        child_profile = self.db.scalar(
            select(ChildProfile).where(ChildProfile.id == child_profile_id)
        )
        if not child_profile:
            raise HTTPException(status_code=404, detail="Child profile not found")

        first_scene = self.db.scalar(
            select(StoryScene)
            .where(StoryScene.story_id == story_id)
            .order_by(StoryScene.scene_order)
            .limit(1)
        )
        if not first_scene:
            raise HTTPException(status_code=404, detail="Story has no scenes")

        session = UserStorySession(
            user_id=user_id,
            child_profile_id=child_profile_id,
            story_id=story_id,
            current_scene_id=first_scene.id,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return self._build_session_scene_response(session.id, first_scene.id)

    def get_current_scene(self, session_id: int) -> SessionSceneRead:
        session = self.db.scalar(
            select(UserStorySession).where(UserStorySession.id == session_id)
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return self._build_session_scene_response(session.id, session.current_scene_id)

    def next_scene(self, session_id: int, current_scene_id: int) -> SessionSceneRead:
        # linear 동화일 시: 선택지 없이 바로 다음 씬으로 이동
        session = self.db.scalar(
            select(UserStorySession).where(UserStorySession.id == session_id)
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        story = self.db.scalar(select(Story).where(Story.id == session.story_id))
        if not story or story.story_type != "linear":
            raise HTTPException(status_code=400, detail="Not a linear story")

        if session.current_scene_id != current_scene_id:
            raise HTTPException(status_code=400, detail="Invalid current scene")

        current_scene = self.db.scalar(
            select(StoryScene).where(StoryScene.id == current_scene_id)
        )
        if not current_scene:
            raise HTTPException(status_code=404, detail="Current scene not found")

        # 다음 장면 결정
        next_scene = None
        if current_scene.next_scene_id:
            next_scene = self.db.scalar(
                select(StoryScene).where(StoryScene.id == current_scene.next_scene_id)
            )
        else:
            # next_scene_id가 없으면 order_index 기반으로 다음 장면 검색
            next_scene = self.db.scalar(
                select(StoryScene)
                .where(StoryScene.story_id == session.story_id)
                .where(StoryScene.scene_order > current_scene.scene_order)
                .order_by(StoryScene.scene_order)
                .limit(1)
            )

        if not next_scene:
            # 다음 장면이 없으면 엔딩 처리 또는 에러
            raise HTTPException(status_code=404, detail="Next scene not found")

        session.current_scene_id = next_scene.id
        self.db.commit()
        self.db.refresh(session)

        return self._build_session_scene_response(session.id, session.current_scene_id)

    def make_choice(self, session_id: int, choice_id: int) -> SessionSceneRead:
        session = self.db.scalar(
            select(UserStorySession).where(UserStorySession.id == session_id)
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        choice = self.db.scalar(select(StoryChoice).where(StoryChoice.id == choice_id))
        if not choice:
            raise HTTPException(status_code=404, detail="Choice not found")

        if choice.scene_id != session.current_scene_id:
            raise HTTPException(
                status_code=400, detail="Invalid choice for current scene"
            )

        # Log the choice
        choice_log = UserChoiceLog(
            session_id=session.id,
            scene_id=session.current_scene_id,
            choice_id=choice.id,
        )
        self.db.add(choice_log)

        # Move to next scene depending on action_type
        if choice.action_type == "generate_scene" or choice.next_scene_id is None:
            # LLM generation is needed
            raise HTTPException(
                status_code=501,
                detail="Dynamic scene generation (Story Agent) is not implemented yet",
            )
        elif choice.action_type == "end_story":
            session.status = "completed"
            self.db.commit()
            # 엔딩 후 현재 장면 그대로 반환 혹은 특수한 응답을 줘야 함
            return self._build_session_scene_response(
                session.id, session.current_scene_id
            )
        elif choice.action_type == "go_to_scene":
            session.current_scene_id = choice.next_scene_id
            self.db.commit()
            self.db.refresh(session)
            return self._build_session_scene_response(
                session.id, session.current_scene_id
            )
        else:
            raise HTTPException(
                status_code=400, detail=f"Unknown action type: {choice.action_type}"
            )

    def _build_session_scene_response(
        self, session_id: int, scene_id: int
    ) -> SessionSceneRead:
        scene = self.db.scalar(select(StoryScene).where(StoryScene.id == scene_id))
        choices = self.db.scalars(
            select(StoryChoice).where(StoryChoice.scene_id == scene_id)
        ).all()

        scene_read = StorySceneRead.model_validate(scene)
        choices_read = [StoryChoiceRead.model_validate(c) for c in choices]

        return SessionSceneRead(
            session_id=session_id,
            current_scene=scene_read,
            choices=choices_read,
        )
