"""JSON-based implementation of the MeetingRoomRepository."""

import os
import threading
from pathlib import Path

from src.domain.aggregates.meeting_room import MeetingRoom
from src.domain.repositories.meeting_room_repository import MeetingRoomRepository
from src.infrastructure.exceptions import StorageConfigurationError


class JsonMeetingRoomRepository(MeetingRoomRepository):
    """JSON file-based implementation of the MeetingRoomRepository.

    This repository stores MeetingRoom aggregates as JSON files on disk.
    It provides persistent storage with thread-safe access and in-memory caching.
    """

    def __init__(self, storage_path: str = "data/meeting_rooms") -> None:
        """Initialize the JSON repository with storage path.

        Args:
            storage_path: Directory path where JSON files will be stored

        Raises:
            StorageConfigurationError: If storage directory cannot be created

        """
        self._storage_path = storage_path
        self._lock = threading.RLock()
        self._cache: dict[str, MeetingRoom] = {}

        self._ensure_storage_directory()

    def _ensure_storage_directory(self) -> None:
        """Ensure the storage directory exists, creating it if necessary.

        Raises:
            StorageConfigurationError: If directory cannot be created

        """
        try:
            Path(self._storage_path).mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError) as e:
            raise StorageConfigurationError(
                f"Cannot create storage directory: {self._storage_path}",
                details={"path": self._storage_path, "error": str(e)},
                cause=e,
            ) from e

    def _get_file_path(self, room_id: str) -> str:
        """Get the file path for a meeting room's JSON file.

        Args:
            room_id: The meeting room ID

        Returns:
            Full path to the JSON file for the meeting room

        """
        return os.path.join(self._storage_path, f"{room_id}.json")

    def _save_to_file(self, meeting_room: MeetingRoom) -> None:
        """Save a MeetingRoom aggregate to a JSON file using atomic writes.

        Args:
            meeting_room: The MeetingRoom aggregate to save

        Raises:
            StorageError: If the file cannot be written

        """
        import json

        file_path = self._get_file_path(meeting_room.id)
        temp_path = f"{file_path}.tmp"

        try:
            # Serialize to JSON using Pydantic's model_dump
            json_data = meeting_room.model_dump(mode="json")

            # Write to temporary file first (atomic write pattern)
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

            # Atomic move to final location
            os.replace(temp_path, file_path)

        except (OSError, PermissionError) as e:
            # Clean up temporary file on error
            if os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass  # Ignore cleanup errors

            from src.infrastructure.exceptions import StorageError

            raise StorageError(
                f"Failed to save meeting room to file: {file_path}",
                details={"room_id": meeting_room.id, "file_path": file_path, "error": str(e)},
                cause=e,
            ) from e

    def _load_from_file(self, room_id: str) -> MeetingRoom | None:
        """Load a MeetingRoom aggregate from a JSON file.

        Args:
            room_id: The ID of the meeting room to load

        Returns:
            The MeetingRoom aggregate if found, otherwise None

        """
        import json

        file_path = self._get_file_path(room_id)

        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, encoding="utf-8") as f:
                json_data = json.load(f)

            # Deserialize from JSON using Pydantic's model_validate
            return MeetingRoom.model_validate(json_data)

        except (OSError, PermissionError, json.JSONDecodeError, ValueError) as e:
            # Create backup of corrupted file for recovery
            self._create_backup_file(file_path)

            # Log error and return None for corrupted/unreadable files
            # In a real application, you'd use proper logging here
            print(f"Warning: Failed to load meeting room {room_id} from {file_path}: {e}")
            return None

    def _create_backup_file(self, file_path: str) -> None:
        """Create a backup of a corrupted file for recovery purposes.

        Args:
            file_path: Path to the file to backup

        """
        backup_path = f"{file_path}.backup"
        try:
            if os.path.exists(file_path):
                # Copy the corrupted file to backup location
                import shutil

                shutil.copy2(file_path, backup_path)
        except OSError:
            # If backup creation fails, continue silently
            # This prevents backup failures from breaking the main operation
            pass

    def save(self, meeting_room: MeetingRoom) -> None:
        """Save a MeetingRoom aggregate to JSON storage.

        If a room with the same ID already exists, it will be updated.
        """
        with self._lock:
            # Save to file
            self._save_to_file(meeting_room)
            # Update cache
            self._cache[meeting_room.id] = meeting_room

    def find_by_id(self, room_id: str) -> MeetingRoom | None:
        """Find a MeetingRoom aggregate by its ID.

        Returns the MeetingRoom if found, otherwise None.
        """
        with self._lock:
            # Check cache first
            if room_id in self._cache:
                return self._cache[room_id]

            # Load from file
            meeting_room = self._load_from_file(room_id)
            if meeting_room is not None:
                # Cache the loaded room
                self._cache[room_id] = meeting_room

            return meeting_room

    def find_all(self) -> list[MeetingRoom]:
        """Retrieve all MeetingRoom aggregates from JSON storage.

        Returns a list of all stored MeetingRoom objects.
        """
        with self._lock:
            # Get all JSON files in storage directory
            all_rooms = []
            storage_path = Path(self._storage_path)

            if not storage_path.exists():
                return all_rooms

            for filename in storage_path.iterdir():
                if filename.suffix != ".json":
                    continue

                room_id = filename.stem

                # Check cache first
                if room_id in self._cache:
                    all_rooms.append(self._cache[room_id])
                else:
                    # Load from file
                    meeting_room = self._load_from_file(room_id)
                    if meeting_room is None:
                        continue
                    # Cache the loaded room
                    self._cache[room_id] = meeting_room
                    all_rooms.append(meeting_room)

            return all_rooms

    def delete(self, room_id: str) -> None:
        """Delete a MeetingRoom aggregate by its ID from JSON storage.

        If the room does not exist, no action is taken.
        """
        with self._lock:
            file_path = self._get_file_path(room_id)

            # Remove from cache
            if room_id in self._cache:
                del self._cache[room_id]

            # Remove file if it exists
            if os.path.exists(file_path):
                try:
                    os.unlink(file_path)
                except OSError:
                    # Ignore errors when deleting (file might be locked, etc.)
                    pass
