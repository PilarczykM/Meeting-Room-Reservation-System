import os


def test_project_structure():
    """
    Tests that the project has the required folder structure.
    """
    # Given
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    expected_dirs = ["src/domain", "src/application", "src/infrastructure", "tests"]

    # When
    missing_dirs = [d for d in expected_dirs if not os.path.isdir(os.path.join(root_dir, d))]

    # Then
    assert not missing_dirs, f"Missing directories: {', '.join(missing_dirs)}"
