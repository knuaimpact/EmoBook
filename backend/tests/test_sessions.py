from fastapi.testclient import TestClient
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.model.child_profile import ChildProfile
from app.model.story import Story
from app.model.story_scene import StoryScene
from app.model.user import User

def test_interactive_session_flow(client: TestClient, db: Session):
    # Setup Data
    user = User(email="test@example.com", password_hash="dummy", name="Test User")
    db.add(user)
    db.commit()

    child = ChildProfile(user_id=user.id, name="Test Child", age=5)
    db.add(child)
    db.commit()

    story = Story(title="Test Story", story_type="interactive")
    db.add(story)
    db.commit()

    scene1 = StoryScene(story_id=story.id, scene_order=0, text="Scene 1")
    scene2 = StoryScene(story_id=story.id, scene_order=1, text="Scene 2")
    db.add(scene1)
    db.add(scene2)
    db.commit()

    # Test Start Session API
    response = client.post(
        f"/api/v1/stories/{story.id}/start",
        json={"child_profile_id": child.id, "user_id": user.id}
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

    story = Story(title="Linear Story", story_type="linear")
    db.add(story)
    db.commit()

    scene1 = StoryScene(story_id=story.id, scene_order=1, text="Scene 1")
    scene2 = StoryScene(story_id=story.id, scene_order=2, text="Scene 2")
    db.add(scene1)
    db.add(scene2)
    db.commit()

    # Test Start Session API
    response = client.post(
        f"/api/v1/stories/{story.id}/start",
        json={"child_profile_id": child.id, "user_id": user.id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["current_scene"]["id"] == scene1.id
    session_id = data["session_id"]

    # Test Next Scene API
    response = client.post(
        f"/api/v1/sessions/{session_id}/next",
        json={"current_scene_id": scene1.id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["current_scene"]["id"] == scene2.id
