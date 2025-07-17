"""Tests for application lifecycle management."""

from unittest.mock import Mock

from src.infrastructure.application import Application


def test_run_with_cli_arguments():
    """Test that run passes arguments to CLI application."""
    app = Application()
    app.bootstrap()

    mock_cli = Mock()
    app.cli_app = mock_cli

    args = ["book", "--room", "A", "--time", "10:00"]
    app.run(args)

    mock_cli.run.assert_called_once_with(args)


def test_shutdown_cleans_up_resources():
    """Test that shutdown cleans up resources properly."""
    app = Application()
    app.bootstrap()

    # Mock some resources
    mock_container = Mock()
    app.container = mock_container

    app.shutdown()

    # Should clean up resources
    assert app.container is None
    assert app.cli_app is None


def test_shutdown_handles_cleanup_errors():
    """Test that shutdown handles cleanup errors gracefully."""
    app = Application()
    app.bootstrap()

    # Mock container that raises error on cleanup
    mock_container = Mock()
    mock_container.cleanup = Mock(side_effect=Exception("Cleanup error"))
    app.container = mock_container

    # Should not raise exception
    app.shutdown()

    # Should still clean up what it can
    assert app.container is None
