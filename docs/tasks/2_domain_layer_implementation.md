## 2. Domain Layer Implementation

### 2.1 Core Domain Entities - TimeSlot
**Branch**: `feature/timeslot-entity`
**Reference**: `{ROOT}/docs/PRD.md Section 6`, {ROOT}/docs/event_storming/_meeting_room_event_storming.mmd (booking sequence diagram), {ROOT}/docs/domain_class_model.mmd

- [x] Create TimeSlot value object in domain/entities/
- [x] Implement TimeSlot with start_time and end_time attributes
- [x] Add validation for time slot consistency (start < end)
- [x] Implement overlap detection method
- [x] Add timezone handling considerations
- [x] Create TimeSlot equality and comparison methods
- [x] **Tests**: Write comprehensive unit tests for TimeSlot validation
- [x] **Tests**: Test overlap detection with various scenarios
- [x] **Tests**: Test edge cases (same start/end, midnight boundary)
- [x] **Acceptance Criteria**: TimeSlot validates time ranges and detects overlaps correctly
- [x] **Commit**

### 2.2 Core Domain Entities - Booking
**Branch**: `feature/booking-entity`
**Reference**: `{ROOT}/docs/PRD.md Section 6`, {ROOT}/docs/event_storming/_meeting_room_event_storming.mmd (booking sequence diagram), {ROOT}/docs/domain_class_model.mmd

- [x] Create Booking entity in domain/entities/
- [x] Implement Booking with booking_id, time_slot, booker, attendees attributes
- [x] Add attendee count validation (4-20 inclusive)
- [x] Implement unique booking ID generation
- [x] Add booking equality and hash methods
- [x] Create booking status tracking if needed
- [x] **Tests**: Write unit tests for Booking creation and validation
- [x] **Tests**: Test attendee count validation edge cases
- [x] **Tests**: Test booking ID uniqueness
- [x] **Acceptance Criteria**: Booking entity enforces all business rules correctly
- [x] **Commit**

### 2.3 Domain Exceptions
**Branch**: `feature/domain-exceptions`
**Reference**: `{ROOT}/docs/PRD.md Section 5`, {ROOT}/docs/event_storming/_meeting_room_event_storming.mmd (error handling in diagrams)

- [x] Create domain/exceptions.py module
- [x] Implement OverlappingBookingError exception
- [x] Implement InvalidAttendeeCountError exception
- [x] Implement BookingNotFoundError exception
- [x] Implement InvalidTimeSlotError exception
- [x] Add descriptive error messages for each exception
- [x] Create base DomainError class
- [x] **Tests**: Test exception creation and message formatting
- [x] **Tests**: Test exception inheritance hierarchy
- [x] **Acceptance Criteria**: All domain exceptions provide clear error messages
- [x] **Commit**

### 2.4 Meeting Room Aggregate Root
**Branch**: `feature/meeting-room-aggregate`
**Reference**: `{ROOT}/docs/PRD.md Section 6`, {ROOT}/docs/event_storming/_meeting_room_event_storming.mmd (all sequence diagrams), {ROOT}/docs/domain_class_model.mmd

- [x] Create MeetingRoom aggregate root in domain/aggregates/
- [x] Implement room capacity constant (20 people)
- [x] Add bookings collection management
- [x] Implement book() method with overlap validation
- [x] Implement cancel() method with booking lookup
- [x] Implement list_bookings() method
- [x] Add private validation methods for business rules
- [x] Ensure aggregate maintains consistency
- [x] **Tests**: Write comprehensive unit tests for all MeetingRoom methods
- [x] **Tests**: Test business rule enforcement (overlaps, attendee limits)
- [x] **Tests**: Test aggregate state consistency
- [x] **Acceptance Criteria**: MeetingRoom enforces all business rules and maintains data integrity
- [x] **Commit**

## Git Workflow Guidelines

### Branch Management
- Start from latest main: `git checkout main && git pull origin main`
- Create feature branches: `git checkout -b feature/task-name`
- Use descriptive branch names with kebab-case (e.g., `feature/user-authentication`, `fix/login-validation`)
- Make frequent commits with clear messages

### Commit Message Format
- feat: new feature implementation
- fix: bug fixes
- test: adding or modifying tests
- docs: documentation changes
- refactor: code refactoring
- style: formatting changes

### Quality Gates
- All tests must pass before push
- Code coverage must be maintained above 90%
- Linting and formatting checks must pass

### Testing Strategy
- Write tests before implementing features (TDD)
- Maintain comprehensive test coverage
- Include unit, integration, and end-to-end tests
- Test all error scenarios and edge cases
- Use property-based testing where applicable
