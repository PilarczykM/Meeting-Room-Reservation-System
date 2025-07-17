# Requirements Document

## Introduction

The CLI Command Registration feature enables users to interact with the Meeting Room Reservation System through command-line interface commands. This feature connects the existing CLI command implementations (BookingCommand, CancellationCommand, ListCommand) with the CLI application by registering them during application bootstrap. It ensures that users can execute booking, cancellation, and listing operations through intuitive command-line interfaces.

## Requirements

### Requirement 1

**User Story:** As a user, I want to see available commands when I run the application without arguments so that I know what operations I can perform.

#### Acceptance Criteria

1. WHEN I run `uv run main.py` without arguments THEN the system SHALL display a help message with all available commands
2. WHEN the help is displayed THEN the system SHALL show command names and their descriptions in a formatted table
3. WHEN no commands are registered THEN the system SHALL display "No commands registered" message
4. WHEN commands are properly registered THEN the system SHALL list "book", "cancel", and "list" commands with descriptions

### Requirement 2

**User Story:** As a user, I want to book a meeting room using the command line so that I can reserve time slots interactively.

#### Acceptance Criteria

1. WHEN I run `uv run main.py book` THEN the system SHALL start the interactive booking process
2. WHEN the booking command executes THEN the system SHALL prompt for start time, end time, booker name, and attendees
3. WHEN I provide valid booking information THEN the system SHALL create the booking and display a success message with booking ID
4. WHEN I provide invalid information THEN the system SHALL display validation errors and allow me to retry
5. WHEN booking conflicts occur THEN the system SHALL display appropriate error messages

### Requirement 3

**User Story:** As a user, I want to cancel a meeting room booking using the command line so that I can remove reservations I no longer need.

#### Acceptance Criteria

1. WHEN I run `uv run main.py cancel` THEN the system SHALL start the interactive cancellation process
2. WHEN the cancellation command executes THEN the system SHALL prompt for the booking ID to cancel
3. WHEN I provide a valid booking ID THEN the system SHALL display booking details and ask for confirmation
4. WHEN I confirm cancellation THEN the system SHALL remove the booking and display a success message
5. WHEN I provide an invalid booking ID THEN the system SHALL display an error message

### Requirement 4

**User Story:** As a user, I want to list all meeting room bookings using the command line so that I can see current reservations.

#### Acceptance Criteria

1. WHEN I run `uv run main.py list` THEN the system SHALL display all current bookings in a formatted table
2. WHEN bookings exist THEN the system SHALL show booking ID, times, booker, attendees, and duration
3. WHEN no bookings exist THEN the system SHALL display a message indicating the room is available
4. WHEN the list is displayed THEN the system SHALL include summary statistics (total bookings, attendees, duration)
5. WHEN I use `uv run main.py list --sort time|booker|attendees` THEN the system SHALL sort the results accordingly

### Requirement 5

**User Story:** As a developer, I want CLI commands to be automatically registered during application bootstrap so that the system properly wires command handlers with the CLI application.

#### Acceptance Criteria

1. WHEN the application bootstraps THEN the system SHALL resolve required services from the dependency injection container
2. WHEN services are resolved THEN the system SHALL create command handler instances with proper dependencies
3. WHEN command handlers are created THEN the system SHALL register them with the CLI application using appropriate command names
4. WHEN command registration fails THEN the system SHALL provide clear error messages and fail gracefully
5. WHEN the application starts successfully THEN all commands SHALL be available for execution