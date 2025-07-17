"""Tests for interruptible input handler."""

from unittest.mock import patch

import pytest

from src.infrastructure.cli.input_handler import InterruptibleInput


class TestInterruptibleInput:
    """Test cases for InterruptibleInput utility."""

    def test_get_input_returns_user_input(self):
        """Test that get_input returns user input normally."""
        with patch("builtins.input", return_value="test input"):
            result = InterruptibleInput.get_input("Enter something: ")
            assert result == "test input"

    def test_get_input_strips_whitespace(self):
        """Test that get_input strips whitespace from input."""
        with patch("builtins.input", return_value="  test input  "):
            result = InterruptibleInput.get_input("Enter something: ")
            assert result == "test input"

    def test_get_input_handles_empty_input(self):
        """Test that get_input handles empty input."""
        with patch("builtins.input", return_value=""):
            result = InterruptibleInput.get_input("Enter something: ")
            assert result == ""

    def test_get_input_raises_keyboard_interrupt_on_sigint(self):
        """Test that get_input raises KeyboardInterrupt when SIGINT is received."""

        def mock_input(prompt):
            # Simulate SIGINT during input
            raise KeyboardInterrupt()

        with patch("builtins.input", side_effect=mock_input):
            with pytest.raises(KeyboardInterrupt):
                InterruptibleInput.get_input("Enter something: ")

    def test_get_confirmation_returns_true_for_yes(self):
        """Test that get_confirmation returns True for 'yes' responses."""
        test_cases = ["y", "yes", "Y", "YES", "Yes"]
        for response in test_cases:
            with patch("builtins.input", return_value=response):
                result = InterruptibleInput.get_confirmation("Confirm? (y/n): ")
                assert result is True

    def test_get_confirmation_returns_false_for_no(self):
        """Test that get_confirmation returns False for 'no' responses."""
        test_cases = ["n", "no", "N", "NO", "No"]
        for response in test_cases:
            with patch("builtins.input", return_value=response):
                result = InterruptibleInput.get_confirmation("Confirm? (y/n): ")
                assert result is False

    def test_get_confirmation_reprompts_for_invalid_input(self):
        """Test that get_confirmation reprompts for invalid input."""
        with patch("builtins.input", side_effect=["invalid", "maybe", "y"]):
            result = InterruptibleInput.get_confirmation("Confirm? (y/n): ")
            assert result is True

    def test_get_confirmation_raises_keyboard_interrupt_on_sigint(self):
        """Test that get_confirmation raises KeyboardInterrupt when SIGINT is received."""

        def mock_input(prompt):
            raise KeyboardInterrupt()

        with patch("builtins.input", side_effect=mock_input):
            with pytest.raises(KeyboardInterrupt):
                InterruptibleInput.get_confirmation("Confirm? (y/n): ")

    def test_get_confirmation_handles_keyboard_interrupt_during_reprompt(self):
        """Test that get_confirmation handles KeyboardInterrupt during reprompt loop."""
        with patch("builtins.input", side_effect=["invalid", KeyboardInterrupt()]):
            with pytest.raises(KeyboardInterrupt):
                InterruptibleInput.get_confirmation("Confirm? (y/n): ")
