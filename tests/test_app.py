import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities as activities_data
from src.app import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activity store after each test."""
    original_activities = copy.deepcopy(activities_data)
    yield
    activities_data.clear()
    activities_data.update(copy.deepcopy(original_activities))


def test_root_redirects_to_index():
    # Arrange
    url = "/"

    # Act
    response = client.get(url, allow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activities_map():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    assert response.json() == activities_data


def test_signup_for_activity_adds_new_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities_data[activity_name]["participants"]


def test_signup_existing_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    existing_email = activities_data[activity_name]["participants"][0]
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_removes_student():
    # Arrange
    activity_name = "Programming Class"
    email = activities_data[activity_name]["participants"][0]
    url = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities_data[activity_name]["participants"]


def test_remove_missing_participant_returns_404():
    # Arrange
    activity_name = "Programming Class"
    email = "unknown@student.edu"
    url = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found for this activity"
