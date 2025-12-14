"""Tests for the Mergington High School Activities API"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

# Create test client
client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint"""

    def test_get_activities_returns_200(self):
        """Test that GET /activities returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_has_expected_activities(self):
        """Test that response contains expected activities"""
        response = client.get("/activities")
        activities = response.json()
        
        assert "Basketball Team" in activities
        assert "Soccer Club" in activities
        assert "Art Club" in activities
        assert "Drama Club" in activities
        assert "Debate Team" in activities
        assert "Math Club" in activities
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_details in activities.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)


class TestSignupEndpoint:
    """Tests for the /activities/{activity_name}/signup endpoint"""

    def test_signup_new_student_returns_200(self):
        """Test that signing up a new student returns 200"""
        response = client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 200

    def test_signup_new_student_adds_to_participants(self):
        """Test that signing up adds the student to participants"""
        response = client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        
        # Verify student was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "newstudent@mergington.edu" in activities["Basketball Team"]["participants"]

    def test_signup_returns_success_message(self):
        """Test that signup returns a success message"""
        response = client.post(
            "/activities/Soccer%20Club/signup",
            params={"email": "player@mergington.edu"}
        )
        data = response.json()
        assert "message" in data
        assert "player@mergington.edu" in data["message"]
        assert "Soccer Club" in data["message"]

    def test_signup_duplicate_student_returns_400(self):
        """Test that signing up a student twice returns 400"""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            "/activities/Art%20Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            "/activities/Art%20Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_invalid_activity_returns_404(self):
        """Test that signing up for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestUnregisterEndpoint:
    """Tests for the /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_student_returns_200(self):
        """Test that unregistering an existing student returns 200"""
        # First sign up
        client.post(
            "/activities/Drama%20Club/signup",
            params={"email": "drama@mergington.edu"}
        )
        
        # Then unregister
        response = client.post(
            "/activities/Drama%20Club/unregister",
            params={"email": "drama@mergington.edu"}
        )
        assert response.status_code == 200

    def test_unregister_removes_student_from_participants(self):
        """Test that unregistering removes the student from participants"""
        email = "removed@mergington.edu"
        activity = "Debate%20Team"
        
        # Sign up
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Verify student is in list
        response = client.get("/activities")
        assert email in response.json()["Debate Team"]["participants"]
        
        # Unregister
        client.post(f"/activities/{activity}/unregister", params={"email": email})
        
        # Verify student is removed
        response = client.get("/activities")
        assert email not in response.json()["Debate Team"]["participants"]

    def test_unregister_returns_success_message(self):
        """Test that unregister returns a success message"""
        email = "unregister@mergington.edu"
        
        # Sign up first
        client.post(
            "/activities/Math%20Club/signup",
            params={"email": email}
        )
        
        # Unregister
        response = client.post(
            "/activities/Math%20Club/unregister",
            params={"email": email}
        )
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_unregister_non_signed_up_student_returns_400(self):
        """Test that unregistering a student who isn't signed up returns 400"""
        response = client.post(
            "/activities/Chess%20Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_invalid_activity_returns_404(self):
        """Test that unregistering from non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/unregister",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestPreconfiguredParticipants:
    """Tests for activities with preconfigured participants"""

    def test_chess_club_has_preconfigured_participants(self):
        """Test that Chess Club has preconfigured participants"""
        response = client.get("/activities")
        activities = response.json()
        
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]

    def test_programming_class_has_preconfigured_participants(self):
        """Test that Programming Class has preconfigured participants"""
        response = client.get("/activities")
        activities = response.json()
        
        assert "emma@mergington.edu" in activities["Programming Class"]["participants"]
        assert "sophia@mergington.edu" in activities["Programming Class"]["participants"]

    def test_gym_class_has_preconfigured_participants(self):
        """Test that Gym Class has preconfigured participants"""
        response = client.get("/activities")
        activities = response.json()
        
        assert "john@mergington.edu" in activities["Gym Class"]["participants"]
        assert "olivia@mergington.edu" in activities["Gym Class"]["participants"]
