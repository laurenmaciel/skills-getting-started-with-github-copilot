"""Tests for activities data and behavior using AAA pattern."""
import pytest


class TestActivityData:
    """Test activity data structure and integrity."""

    def test_all_activities_have_required_fields(self, client):
        """
        ARRANGE: Set up the test client
        ACT: Retrieve all activities
        ASSERT: Verify all activities have required fields
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert required_fields.issubset(activity_data.keys()), \
                f"{activity_name} missing required fields"

    def test_max_participants_is_positive_integer(self, client):
        """
        ARRANGE: Set up the test client
        ACT: Retrieve all activities
        ASSERT: Verify max_participants is a positive integer
        """
        # Arrange - implicit via fixture

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0

    def test_participants_count_not_exceeds_max(self, client):
        """
        ARRANGE: Set up the test client
        ACT: Retrieve all activities
        ASSERT: Verify current participants don't exceed max capacity
        """
        # Arrange - implicit via fixture

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert len(activity_data["participants"]) <= activity_data["max_participants"], \
                f"{activity_name} has more participants than capacity allows"

    @pytest.mark.parametrize("activity_name", [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Soccer Club",
        "Art Club",
        "Drama Club",
        "Debate Club",
        "Science Club"
    ])
    def test_specific_activities_exist(self, client, activity_name):
        """
        ARRANGE: Set up the test client and parametrized activity name
        ACT: Retrieve all activities
        ASSERT: Verify the specific activity exists in the system
        """
        # Arrange - implicit via fixture and parametrize

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert activity_name in activities

    def test_chess_club_has_correct_schedule(self, client):
        """
        ARRANGE: Set up the test client
        ACT: Retrieve all activities
        ASSERT: Verify Chess Club has the correct schedule
        """
        # Arrange
        expected_schedule = "Fridays, 3:30 PM - 5:00 PM"

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert activities["Chess Club"]["schedule"] == expected_schedule

    def test_programming_class_has_correct_max_participants(self, client):
        """
        ARRANGE: Set up the test client
        ACT: Retrieve all activities
        ASSERT: Verify Programming Class has the correct max participants
        """
        # Arrange
        expected_max = 20

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert activities["Programming Class"]["max_participants"] == expected_max

    def test_all_participants_are_email_strings(self, client):
        """
        ARRANGE: Set up the test client
        ACT: Retrieve all activities
        ASSERT: Verify all participants are email strings
        """
        # Arrange - implicit via fixture

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation