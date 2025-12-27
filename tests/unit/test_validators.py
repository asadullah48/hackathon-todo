"""Unit tests for input validators."""

import pytest

from src.lib.validators import validate_title, validate_description, validate_task_id


class TestValidateTitle:
    """Tests for title validation."""

    def test_valid_title(self) -> None:
        """Test that a valid title passes validation."""
        is_valid, error = validate_title("Buy groceries")
        assert is_valid is True
        assert error == ""

    def test_empty_title(self) -> None:
        """Test that empty title fails validation."""
        is_valid, error = validate_title("")
        assert is_valid is False
        assert error == "Title cannot be empty"

    def test_whitespace_only_title(self) -> None:
        """Test that whitespace-only title fails validation."""
        is_valid, error = validate_title("   ")
        assert is_valid is False
        assert error == "Title cannot be empty"

    def test_title_at_max_length(self) -> None:
        """Test that title at max length (200) passes."""
        title = "a" * 200
        is_valid, error = validate_title(title)
        assert is_valid is True
        assert error == ""

    def test_title_exceeds_max_length(self) -> None:
        """Test that title > 200 chars fails validation."""
        title = "a" * 201
        is_valid, error = validate_title(title)
        assert is_valid is False
        assert error == "Title exceeds 200 characters"


class TestValidateDescription:
    """Tests for description validation."""

    def test_valid_description(self) -> None:
        """Test that a valid description passes validation."""
        is_valid, error = validate_description("Some description")
        assert is_valid is True
        assert error == ""

    def test_empty_description(self) -> None:
        """Test that empty description is valid."""
        is_valid, error = validate_description("")
        assert is_valid is True
        assert error == ""

    def test_description_at_max_length(self) -> None:
        """Test that description at max length (1000) passes."""
        description = "b" * 1000
        is_valid, error = validate_description(description)
        assert is_valid is True
        assert error == ""

    def test_description_exceeds_max_length(self) -> None:
        """Test that description > 1000 chars fails validation."""
        description = "b" * 1001
        is_valid, error = validate_description(description)
        assert is_valid is False
        assert error == "Description exceeds 1000 characters"


class TestValidateTaskId:
    """Tests for task ID validation."""

    def test_valid_task_id(self) -> None:
        """Test that a valid positive integer ID passes."""
        is_valid, task_id, error = validate_task_id("1")
        assert is_valid is True
        assert task_id == 1
        assert error == ""

    def test_valid_large_task_id(self) -> None:
        """Test that large IDs are valid."""
        is_valid, task_id, error = validate_task_id("999")
        assert is_valid is True
        assert task_id == 999
        assert error == ""

    def test_zero_task_id(self) -> None:
        """Test that zero ID fails validation."""
        is_valid, task_id, error = validate_task_id("0")
        assert is_valid is False
        assert task_id is None
        assert error == "Invalid ID"

    def test_negative_task_id(self) -> None:
        """Test that negative ID fails validation."""
        is_valid, task_id, error = validate_task_id("-1")
        assert is_valid is False
        assert task_id is None
        assert error == "Invalid ID"

    def test_non_numeric_task_id(self) -> None:
        """Test that non-numeric input fails validation."""
        is_valid, task_id, error = validate_task_id("abc")
        assert is_valid is False
        assert task_id is None
        assert error == "Invalid ID format"

    def test_float_task_id(self) -> None:
        """Test that float string fails validation."""
        is_valid, task_id, error = validate_task_id("1.5")
        assert is_valid is False
        assert task_id is None
        assert error == "Invalid ID format"

    def test_empty_task_id(self) -> None:
        """Test that empty string fails validation."""
        is_valid, task_id, error = validate_task_id("")
        assert is_valid is False
        assert task_id is None
        assert error == "Invalid ID format"
