"""Tests for FastAPI application endpoints using AAA (Arrange-Act-Assert) pattern."""
import pytest


class TestRootEndpoint:
    """Test the root endpoint."""

    def test_root_redirects_to_static(self, client):
        """
        ARRANGE: No special setup needed, using test client fixture
        ACT: Make a GET request to the root endpoint
        ASSERT: Verify the response redirects to /static/index.html
        """
        # Arrange - implicit via fixture

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Test the GET /activities endpoint."""

    def test_get_activities_success(self, client):
        """
        ARRANGE: Set up the test client
        ACT: Retrieve all activities
        ASSERT: Verify we get a successful response with activities
        """
        # Arrange - implicit via fixture

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_contains_required_fields(self, client):
        """
        ARRANGE: Set up the test client
        ACT: Retrieve all activities
        ASSERT: Verify each activity contains required fields
        """
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data, f"Activity '{activity_name}' missing field '{field}'"

    def test_get_activities_participants_is_list(self, client):
        """
        ARRANGE: Set up the test client
        ACT: Retrieve all activities
        ASSERT: Verify participants field is a list
        """
        # Arrange - implicit via fixture

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_max_participants_is_integer(self, client):
        """
        ARRANGE: Set up the test client
        ACT: Retrieve all activities
        ASSERT: Verify max_participants is an integer
        """
        # Arrange - implicit via fixture

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0


class TestActivitySignup:
    """Test the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client, existing_activity, sample_email):
        """
        ARRANGE: Prepare test data with existing activity and new email
        ACT: Sign up the new email for the activity
        ASSERT: Verify successful signup with correct response message
        """
        # Arrange - implicit via fixtures

        # Act
        response = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": sample_email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]
        assert existing_activity in data["message"]

    def test_signup_activity_not_found(self, client, non_existent_activity, sample_email):
        """
        ARRANGE: Prepare data for a non-existent activity
        ACT: Attempt to sign up for the non-existent activity
        ASSERT: Verify we get a 404 error with correct message
        """
        # Arrange - implicit via fixtures

        # Act
        response = client.post(
            f"/activities/{non_existent_activity}/signup",
            params={"email": sample_email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_student(self, client, existing_activity):
        """
        ARRANGE: Get an existing participant email from an activity
        ACT: Attempt to sign up the same email again
        ASSERT: Verify we get a 400 error indicating duplicate signup
        """
        # Arrange
        existing_email = "michael@mergington.edu"  # Already signed up for Chess Club

        # Act
        response = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": existing_email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Student already signed up" in data["detail"]

    def test_signup_adds_participant_to_activity(self, client, existing_activity, sample_email):
        """
        ARRANGE: Get current participants count before signup
        ACT: Sign up a new student and retrieve the activity
        ASSERT: Verify the participant count increased by one
        """
        # Arrange
        response_before = client.get("/activities")
        initial_count = len(response_before.json()[existing_activity]["participants"])

        # Act
        client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": sample_email}
        )
        response_after = client.get("/activities")
        final_count = len(response_after.json()[existing_activity]["participants"])

        # Assert
        assert final_count == initial_count + 1
        assert sample_email in response_after.json()[existing_activity]["participants"]


class TestRemoveParticipant:
    """Test the DELETE /activities/{activity_name}/remove endpoint."""

    def test_remove_participant_success(self, client, existing_activity, sample_email):
        """
        ARRANGE: First sign up a participant, then prepare to remove them
        ACT: Remove the participant from the activity
        ASSERT: Verify removal was successful with correct message
        """
        # Arrange - First sign up the participant
        client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": sample_email}
        )

        # Act
        response = client.delete(
            f"/activities/{existing_activity}/remove",
            params={"email": sample_email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]
        assert existing_activity in data["message"]

    def test_remove_activity_not_found(self, client, non_existent_activity, sample_email):
        """
        ARRANGE: Prepare data for a non-existent activity
        ACT: Attempt to remove a participant from the non-existent activity
        ASSERT: Verify we get a 404 error with correct message
        """
        # Arrange - implicit via fixtures

        # Act
        response = client.delete(
            f"/activities/{non_existent_activity}/remove",
            params={"email": sample_email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_remove_participant_not_found(self, client, existing_activity):
        """
        ARRANGE: Prepare data for a participant not in the activity
        ACT: Attempt to remove a non-existent participant
        ASSERT: Verify we get a 404 error with correct message
        """
        # Arrange
        nonexistent_email = "nonexistent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{existing_activity}/remove",
            params={"email": nonexistent_email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Participant not found" in data["detail"]

    def test_remove_participant_actually_removes(self, client, existing_activity, sample_email):
        """
        ARRANGE: Sign up a participant and get initial count
        ACT: Remove the participant from the activity
        ASSERT: Verify the participant is no longer in the activity
        """
        # Arrange - Sign up first
        client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": sample_email}
        )
        response_before = client.get("/activities")
        initial_count = len(response_before.json()[existing_activity]["participants"])

        # Act
        client.delete(
            f"/activities/{existing_activity}/remove",
            params={"email": sample_email}
        )
        response_after = client.get("/activities")
        final_count = len(response_after.json()[existing_activity]["participants"])

        # Assert
        assert final_count == initial_count - 1
        assert sample_email not in response_after.json()[existing_activity]["participants"]