# Implementation Plan

- [ ] 1. Create interruptible input utility module
  - Create `src/infrastructure/cli/input_handler.py` with InterruptibleInput class
  - Implement `get_input()` method that can be interrupted by signals
  - Implement `get_confirmation()` method for yes/no prompts with signal handling
  - Add proper error handling and fallback to standard input if needed
  - _Requirements: 1.1, 1.2, 3.1, 3.2_

- [ ] 2. Enhance signal handler in main entry point
  - Modify signal handler in `main.py` to force immediate exit after graceful shutdown attempt
  - Ensure proper exit codes are returned (130 for SIGINT, 1 for SIGTERM)
  - Add robust error handling for signal handler failures
  - Maintain existing graceful shutdown functionality
  - _Requirements: 1.3, 1.4, 1.5, 3.3_

- [ ] 3. Update booking command to use interruptible input
  - Replace all `input()` calls in `src/infrastructure/cli/commands/booking_command.py` with InterruptibleInput methods
  - Update `_get_datetime_input()` method to use interruptible input
  - Update `_get_attendees_input()` method to use interruptible input
  - Update confirmation prompts to use interruptible confirmation method
  - Ensure KeyboardInterrupt exceptions are properly handled and propagated
  - _Requirements: 2.1, 2.5, 3.4, 3.5_

- [ ] 4. Update cancellation command to use interruptible input
  - Replace all `input()` calls in `src/infrastructure/cli/commands/cancellation_command.py` with InterruptibleInput methods
  - Update `_get_booking_id_input()` method to use interruptible input
  - Update `_confirm_cancellation()` method to use interruptible confirmation
  - Ensure KeyboardInterrupt exceptions are properly handled and propagated
  - _Requirements: 2.2, 2.5, 3.4, 3.5_

- [ ] 5. Create unit tests for interruptible input utility
  - Write tests for `InterruptibleInput.get_input()` method with normal input
  - Write tests for signal interruption during input operations
  - Write tests for `InterruptibleInput.get_confirmation()` method with various responses
  - Write tests for fallback behavior when signal handling fails
  - Test error handling and edge cases
  - _Requirements: 1.1, 1.2, 3.1_

- [ ] 6. Create unit tests for enhanced signal handling
  - Write tests for enhanced signal handler with immediate exit functionality
  - Test SIGINT handling returns exit code 130
  - Test SIGTERM handling returns exit code 1
  - Test multiple signal scenarios and cleanup during signal handling
  - Test graceful degradation when signal handler encounters errors
  - _Requirements: 1.3, 1.4, 1.5, 3.3_

- [ ] 7. Create integration tests for CLI command signal handling
  - Write tests for booking command interruption at various input stages
  - Write tests for cancellation command interruption at various input stages
  - Test that normal command flow remains unaffected by signal handling changes
  - Test that existing error handling continues to work properly
  - Verify consistent signal handling behavior across all commands
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.4, 3.5_

- [ ] 8. Update existing CLI command tests
  - Modify existing tests in `tests/infrastructure/cli/commands/` to account for new input handling
  - Update test mocks to work with InterruptibleInput instead of built-in input
  - Ensure all existing test scenarios continue to pass
  - Add test cases for KeyboardInterrupt handling in command tests
  - _Requirements: 3.4, 3.5_