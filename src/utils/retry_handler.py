from typing import Dict, Any, Callable
import time

class RetryHandler:
    """Provides automated retry logic for transient API failures."""

    def __init__(self, max_retries: int = 3, delay: float = 2.0):
        self.max_retries = max_retries
        self.delay = delay

    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        Executes a function with a retry mechanism.
        """
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                print(f"Attempt {attempt + 1} failed: {e}. Retrying in {self.delay}s...")
                time.sleep(self.delay)

        print(f"All {self.max_retries} retry attempts failed.")
        raise last_exception
