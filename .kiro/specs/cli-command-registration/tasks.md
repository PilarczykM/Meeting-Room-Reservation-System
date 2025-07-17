# Implementation Plan

- [x] 1. Implement CLI command registration infrastructure
  - Add import statements for CLI command classes in application.py
  - Create _register_cli_commands method to coordinate command registration
  - Add error handling for command registration failures with ApplicationError
  - Implement service scope management for command handler creation
  - _Requirements: 5.1, 5.2, 5.4_

- [x] 2. Implement individual command registration methods
  - Create _register_booking_command method that resolves BookingService and creates BookingCommand instance
  - Create _register_cancellation_command method that resolves CancellationService and QueryService
  - Create _register_list_command method that resolves QueryService and creates ListCommand instance
  - Register each command with CLI application using appropriate command names ("book", "cancel", "list")
  - _Requirements: 2.1, 3.1, 4.1, 5.3_

- [x] 3. Integrate command registration with application bootstrap
  - Modify _create_cli_app method to call _register_cli_commands after creating CLIApp instance
  - Add exception handling to catch and wrap command registration errors as ApplicationError
  - Ensure command registration happens after service configuration is complete
  - Test that application bootstrap fails gracefully if command registration fails
  - _Requirements: 5.1, 5.4, 5.5_

- [x] 4. Validate command registration functionality
  - Write unit test to verify all three commands are registered with correct names
  - Write unit test to verify command handlers are callable and accept args parameter
  - Write unit test to verify service resolution works correctly during command registration
  - Write integration test to verify commands are available after application bootstrap
  - _Requirements: 1.4, 2.1, 3.1, 4.1_

- [x] 5. Test CLI help display functionality
  - Write test to verify help message displays all registered commands when no arguments provided
  - Write test to verify command descriptions are shown in formatted table
  - Write test to verify "book", "cancel", and "list" commands appear in help output
  - Manually test that `uv run main.py` shows available commands instead of "No commands registered"
  - _Requirements: 1.1, 1.2, 1.4_

- [x] 6. Test end-to-end command execution
  - Write integration test that executes `uv run main.py book` and verifies BookingCommand.execute is called
  - Write integration test that executes `uv run main.py cancel` and verifies CancellationCommand.execute is called  
  - Write integration test that executes `uv run main.py list` and verifies ListCommand.execute is called
  - Manually test each command to ensure interactive prompts work correctly
  - _Requirements: 2.1, 2.2, 3.1, 3.2, 4.1, 4.2_

- [x] 7. Test error handling and edge cases
  - Write test to verify graceful handling when required services are not registered in container
  - Write test to verify application startup fails with clear error message if command registration fails
  - Write test to verify unknown command handling still works correctly
  - Test command execution with various argument combinations
  - _Requirements: 2.4, 2.5, 3.5, 5.4_

- [ ] 8. Validate booking flow end-to-end
  - Test complete booking flow: start app, run book command, enter valid data, confirm booking creation
  - Test booking validation: invalid dates, invalid attendee counts, overlapping bookings
  - Test booking cancellation: successful cancellation and error cases
  - Verify booking data persistence and retrieval through list command
  - _Requirements: 2.2, 2.3, 2.4, 2.5_

- [-] 9. Validate cancellation flow end-to-end  
  - Test complete cancellation flow: create booking, run cancel command, enter booking ID, confirm cancellation
  - Test cancellation error cases: invalid booking ID, booking not found
  - Test cancellation confirmation workflow and user interaction
  - Verify cancelled bookings are removed and no longer appear in list command
  - _Requirements: 3.2, 3.3, 3.4, 3.5_

- [ ] 10. Validate listing flow end-to-end
  - Test list command with no bookings shows appropriate empty state message
  - Test list command with bookings shows formatted table with all booking details
  - Test list command sorting options (--sort time, --sort booker, --sort attendees)
  - Test list command summary statistics display (total bookings, attendees, duration)
  - _Requirements: 4.2, 4.3, 4.4, 4.5_