from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from user.child_profile_model import ChildProfile
from story.story_model import Story
from story.story_scene_model import StoryScene
from user.user_model import User
from voice.voice_profile_model import VoiceProfile


def test_interactive_session_flow(client: TestClient, db: Session):
    # Setup Data
    user = User(email="test@example.com", password_hash="dummy", name="Test User")
    db.add(user)
    db.commit()

    child = ChildProfile(user_id=user.id, name="Test Child", age=5)
    db.add(child)
    db.commit()

    voice = VoiceProfile(
        user_id=user.id,
        profile_name="Dad",
        sample_audio_url="dummy",
        sample_audio_object_key="dummy",
    )
    db.add(voice)
    db.commit()

    story = Story(title="Test Story", story_type="interactive")
    db.add(story)
    db.commit()

    scene1 = StoryScene(
        story_id=story.id, scene_order=0, text="Scene 1", scene_key="scene1"
    )
    scene2 = StoryScene(
        story_id=story.id, scene_order=1, text="Scene 2", scene_key="scene2"
    )
    db.add(scene1)
    db.add(scene2)
    db.commit()

    # Test Start Session API
    response = client.post(
        f"/api/v1/stories/{story.id}/start",
        json={
            "child_profile_id": child.id,
            "user_id": user.id,
            "voice_profile_id": voice.id,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["current_scene"]["id"] == scene1.id
    session_id = data["session_id"]

    # Test Get Current Scene API
    response = client.get(f"/api/v1/sessions/{session_id}/current-scene")
    assert response.status_code == 200
    assert response.json()["current_scene"]["id"] == scene1.id


def test_linear_session_flow(client: TestClient, db: Session):
    # Setup Data
    user = User(email="linear@example.com", password_hash="dummy", name="Linear User")
    db.add(user)
    db.commit()

    child = ChildProfile(user_id=user.id, name="Linear Child", age=5)
    db.add(child)
    db.commit()

    voice = VoiceProfile(
        user_id=user.id,
        profile_name="Mom",
        sample_audio_url="dummy",
        sample_audio_object_key="dummy",
    )
    db.add(voice)
    db.commit()

    story = Story(title="Linear Story", story_type="linear")
    db.add(story)
    db.commit()

    scene1 = StoryScene(
        story_id=story.id, scene_order=1, text="Scene 1", scene_key="scene1"
    )
    scene2 = StoryScene(
        story_id=story.id, scene_order=2, text="Scene 2", scene_key="scene2"
    )
    db.add(scene1)
    db.add(scene2)
    db.commit()

    # Test Start Session API
    response = client.post(
        f"/api/v1/stories/{story.id}/start",
        json={
            "child_profile_id": child.id,
            "user_id": user.id,
            "voice_profile_id": voice.id,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["current_scene"]["id"] == scene1.id
    session_id = data["session_id"]

    # Test Next Scene API
    response = client.post(
        f"/api/v1/sessions/{session_id}/next", json={"current_scene_id": scene1.id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["current_scene"]["id"] == scene2.id
