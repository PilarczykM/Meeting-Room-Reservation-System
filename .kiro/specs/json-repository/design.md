# Design Document

## Overview

The JSON repository implementation will provide persistent storage for meeting room data using JSON files on disk. It will maintain the same interface as the existing in-memory repository while adding file-based persistence. The design leverages Pydantic's built-in JSON serialization capabilities and follows the existing DDD architecture patterns.

## Architecture

### Storage Strategy
- **Single JSON file per meeting room**: Each meeting room will be stored as a separate JSON file
- **Atomic writes**: Use temporary files and atomic moves to prevent corruption during writes
- **Lazy loading**: Load data from disk only when needed, cache in memory for performance
- **Write-through caching**: Immediately persist changes to disk while maintaining in-memory cache

### File Structure
```
data/
├── meeting_rooms/
│   ├── {room_id_1}.json
│   ├── {room_id_2}.json
│   └── ...
└── .gitkeep
```

### JSON Schema
Each meeting room JSON file will contain the serialized MeetingRoom aggregate:
```json
{
  "id": "uuid-string",
  "capacity": 20,
  "bookings": [
    {
      "booking_id": "uuid-string",
      "time_slot": {
        "start_time": "2024-01-01T10:00:00+00:00",
        "end_time": "2024-01-01T11:00:00+00:00"
      },
      "booker": "John Doe",
      "attendees": 8
    }
  ]
}
```

## Components and Interfaces

### JsonMeetingRoomRepository
**Location**: `src/infrastructure/repositories/json_repository.py`

**Responsibilities**:
- Implement `MeetingRoomRepository` interface
- Handle JSON serialization/deserialization using Pydantic
- Manage file I/O operations with error handling
- Provide thread-safe access using read-write locks
- Maintain in-memory cache for performance

**Key Methods**:
```python
class JsonMeetingRoomRepository(MeetingRoomRepository):
    def __init__(self, storage_path: str = "data/meeting_rooms")
    def save(self, meeting_room: MeetingRoom) -> None
    def find_by_id(self, room_id: str) -> MeetingRoom | None
    def find_all(self) -> list[MeetingRoom]
    def delete(self, room_id: str) -> None
    def _load_from_file(self, room_id: str) -> MeetingRoom | None
    def _save_to_file(self, meeting_room: MeetingRoom) -> None
    def _ensure_storage_directory(self) -> None
```

### Configuration Integration
**Location**: `src/infrastructure/config/models.py`

Add storage configuration to existing config models:
```python
class StorageConfig(BaseModel):
    type: str = "json"  # future: could support "memory", "database"
    path: str = "data/meeting_rooms"
```

### Service Configuration Update
**Location**: `src/infrastructure/service_configurator.py`

Update dependency injection to use JSON repository:
```python
def configure_repositories(container: Container, config: AppConfig) -> None:
    if config.storage.type == "json":
        container.register_singleton(
            MeetingRoomRepository,
            lambda: JsonMeetingRoomRepository(config.storage.path)
        )
    else:  # fallback to in-memory
        container.register_singleton(
            MeetingRoomRepository,
            InMemoryMeetingRoomRepository
        )
```

## Data Models

### Serialization Strategy
- **Leverage Pydantic**: Use `model_dump()` and `model_validate()` for JSON conversion
- **Handle datetime serialization**: Ensure proper ISO format with timezone information
- **Preserve UUIDs**: Maintain string representation of UUIDs in JSON

### Example Serialization Code
```python
# Serialize to JSON
json_data = meeting_room.model_dump(mode='json')
with open(file_path, 'w') as f:
    json.dump(json_data, f, indent=2, ensure_ascii=False)

# Deserialize from JSON
with open(file_path, 'r') as f:
    json_data = json.load(f)
meeting_room = MeetingRoom.model_validate(json_data)
```

## Error Handling

### File Operation Errors
- **FileNotFoundError**: Return None for missing meeting rooms, log info message
- **PermissionError**: Raise custom `StorageError` with clear message
- **JSONDecodeError**: Log error, treat as missing file, return None
- **OSError**: Raise custom `StorageError` for disk space, network issues

### Custom Exceptions
**Location**: `src/infrastructure/exceptions.py`

```python
class StorageError(Exception):
    """Raised when storage operations fail."""
    pass

class StorageConfigurationError(StorageError):
    """Raised when storage is misconfigured."""
    pass
```

### Error Recovery Strategy
1. **Corrupted files**: Move to `.backup` extension, start fresh
2. **Permission issues**: Provide clear error messages with suggested fixes
3. **Disk space**: Fail fast with actionable error message
4. **Directory creation**: Auto-create missing directories with proper permissions

## Testing Strategy

### Unit Tests
**Location**: `tests/infrastructure/repositories/test_json_repository.py`

**Test Categories**:
1. **Basic CRUD operations**: Save, find, delete meeting rooms
2. **Serialization**: Proper JSON format, datetime handling, UUID preservation
3. **File operations**: Directory creation, atomic writes, file permissions
4. **Error handling**: Corrupted files, missing directories, permission errors
5. **Thread safety**: Concurrent read/write operations
6. **Configuration**: Different storage paths, relative/absolute paths

### Integration Tests
**Location**: `tests/infrastructure/repositories/test_json_repository_integration.py`

**Test Scenarios**:
1. **End-to-end persistence**: Create booking, restart "application", verify booking exists
2. **Multiple meeting rooms**: Ensure proper file separation
3. **Large datasets**: Performance with many bookings
4. **Configuration integration**: Verify DI container uses correct repository

### Test Fixtures
```python
@pytest.fixture
def temp_storage_path(tmp_path):
    """Provide temporary directory for JSON storage tests."""
    return str(tmp_path / "test_meeting_rooms")

@pytest.fixture
def json_repository(temp_storage_path):
    """Provide JsonMeetingRoomRepository with temporary storage."""
    return JsonMeetingRoomRepository(temp_storage_path)
```

### Performance Considerations
- **Benchmark file I/O**: Measure read/write performance with various booking counts
- **Memory usage**: Monitor in-memory cache size with large datasets
- **Concurrent access**: Test performance under concurrent load

## Implementation Notes

### Thread Safety Implementation
- Use `threading.RLock()` for read-write lock semantics
- Allow multiple concurrent reads
- Exclusive access for writes
- Cache invalidation on writes

### Atomic Write Pattern
```python
def _save_to_file(self, meeting_room: MeetingRoom) -> None:
    file_path = self._get_file_path(meeting_room.id)
    temp_path = f"{file_path}.tmp"
    
    try:
        # Write to temporary file
        with open(temp_path, 'w') as f:
            json.dump(meeting_room.model_dump(mode='json'), f, indent=2)
        
        # Atomic move to final location
        os.replace(temp_path, file_path)
    except Exception:
        # Clean up temporary file on error
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise
```

### Configuration Defaults
- **Default storage path**: `data/meeting_rooms` (relative to project root)
- **File permissions**: 644 for files, 755 for directories
- **JSON formatting**: Indented for human readability
- **Encoding**: UTF-8 with BOM handling