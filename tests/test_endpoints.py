"""
Integration tests for FastAPI endpoints using the AAA (Arrange-Act-Assert) pattern.

Tests cover:
- GET / - Root endpoint (redirect)
- GET /activities - List all activities
- POST /activities/{activity_name}/signup - Sign up for an activity
- DELETE /activities/{activity_name}/unregister - Unregister from an activity
"""

import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """
        Arrange: Client is ready
        Act: Make GET request to root
        Assert: Response redirects to /static/index.html
        """
        # Arrange
        # client fixture is provided by conftest.py

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_list(self, client):
        """
        Arrange: Client is ready
        Act: Make GET request to /activities
        Assert: Returns 200 with list of activities
        """
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Soccer Club",
            "Art Club",
            "Drama Club",
            "Debate Club",
            "Science Club"
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        for activity_name in expected_activities:
            assert activity_name in activities

    def test_get_activities_includes_required_fields(self, client):
        """
        Arrange: Client is ready
        Act: Make GET request to /activities
        Assert: Each activity has required fields
        """
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        """
        Arrange: Prepare email and activity name
        Act: Make POST request to signup endpoint
        Assert: Returns 200 with success message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    def test_signup_activity_not_found(self, client):
        """
        Arrange: Prepare non-existent activity name and email
        Act: Make POST request to signup endpoint
        Assert: Returns 404 Activity not found
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_student_already_enrolled(self, client):
        """
        Arrange: Use email already enrolled in Chess Club
        Act: Try to signup the same student again
        Assert: Returns 400 with already signed up message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club participants

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_multiple_activities(self, client):
        """
        Arrange: Use a new email and different activity names
        Act: Sign up for first activity, then second activity
        Assert: Both signups succeed
        """
        # Arrange
        email = "versatile@mergington.edu"
        activity_1 = "Chess Club"
        activity_2 = "Programming Class"

        # Act
        response1 = client.post(
            f"/activities/{activity_1}/signup",
            params={"email": email}
        )
        response2 = client.post(
            f"/activities/{activity_2}/signup",
            params={"email": email}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["message"] == f"Signed up {email} for {activity_1}"
        assert response2.json()["message"] == f"Signed up {email} for {activity_2}"


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client):
        """
        Arrange: Sign up a student, then prepare to unregister
        Act: Make DELETE request to unregister
        Assert: Returns 200 with success message
        """
        # Arrange
        activity_name = "Drama Club"
        email = "testuser@mergington.edu"
        # First, sign up
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

    def test_unregister_activity_not_found(self, client):
        """
        Arrange: Prepare non-existent activity and email
        Act: Make DELETE request to unregister
        Assert: Returns 404 Activity not found
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_student_not_enrolled(self, client):
        """
        Arrange: Use email not enrolled in the activity
        Act: Try to unregister
        Assert: Returns 400 with participant not found message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notenrolled@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Participant not found in this activity"

    def test_unregister_twice_fails_on_second_attempt(self, client):
        """
        Arrange: Sign up, unregister successfully
        Act: Try to unregister again
        Assert: Second unregister returns 400
        """
        # Arrange
        activity_name = "Debate Club"
        email = "twiceuser@mergington.edu"
        # Sign up and unregister successfully
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Participant not found in this activity"
