from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.model.story import Story
from app.model.story_scene import StoryScene
from app.model.user import User


def main() -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.email == "parent@example.com"))
        if user is None:
            db.add(User(email="parent@example.com", name="Demo Parent"))

        story = db.scalar(select(Story).where(Story.title == "달빛 숲의 작은 별"))
        if story is None:
            story = Story(
                title="달빛 숲의 작은 별",
                summary="길을 잃은 작은 별이 숲속 친구들의 도움으로 하늘로 돌아가는 이야기",
                age_range="3-6",
            )
            story.scenes = [
                StoryScene(
                    scene_order=1,
                    title="별이 떨어진 밤",
                    text="깊은 밤, 작은 별 하나가 달빛 숲으로 살포시 내려왔어요.",
                ),
                StoryScene(
                    scene_order=2,
                    title="숲속 친구들",
                    text="토끼와 부엉이는 작은 별을 위해 가장 높은 언덕을 찾아주기로 했어요.",
                ),
                StoryScene(
                    scene_order=3,
                    title="다시 하늘로",
                    text="작은 별은 친구들에게 고맙다고 인사하고 반짝이며 하늘로 올라갔어요.",
                ),
            ]
            db.add(story)

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()

