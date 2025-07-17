"""Interruptible input utility for CLI operations."""


class InterruptibleInput:
    """Provides input functionality that can be interrupted by signals."""

    @staticmethod
    def get_input(prompt: str) -> str:
        """Get user input that can be interrupted by signals.

        Args:
            prompt: The prompt to display to the user

        Returns:
            User input string with whitespace stripped

        Raises:
            KeyboardInterrupt: When SIGINT is received

        """
        user_input = input(prompt)
        return user_input.strip()

    @staticmethod
    def get_confirmation(prompt: str) -> bool:
        """Get yes/no confirmation that can be interrupted by signals.

        Args:
            prompt: The confirmation prompt

        Returns:
            True for yes, False for no

        Raises:
            KeyboardInterrupt: When SIGINT is received

        """
        while True:
            response = input(prompt).strip().lower()
            if response in ["y", "yes"]:
                return True
            elif response in ["n", "no"]:
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")
                continue
