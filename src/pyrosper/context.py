from abc import ABC, abstractmethod
from contextlib import ContextDecorator
from contextvars import ContextVar
from typing import Optional
from .pyrosper import Pyrosper

instance_storage: ContextVar[Optional['Pyrosper']] = ContextVar("pyrosper_instance_storage", default=None)

def get_current() -> 'Pyrosper':
    """Get the current pyrosper instance from context."""
    result: Optional['Pyrosper'] = instance_storage.get()
    if not result:
        raise RuntimeError("No pyrosper instance found in context")
    return result


class BaseContext(ABC, ContextDecorator):
    """
    Context manager and decorator for Pyrosper context isolation.
    
    This class can and should be extended to provide custom context setup and teardown.
    It automatically handles context variable management and cleanup.
    
    Usage as context manager:
        with BaseContext() as pyrosper:
            # Use pyrosper instance
            pass
    
    Usage as decorator:
        @BaseContext()
        def my_function():
            pyrosper = get_current_pyrosper()
            # Use pyrosper instance
            pass
    """
    
    def __init__(self):
        self.instance_token = None
        self.pyrosper_instance = None

    @abstractmethod
    def setup(self) -> 'Pyrosper':
        """
        Setup and return pyrosper. Override this method in subclasses to provide custom setup.
        
        Returns:
            The pyrosper instance to use in this context.
        """
        # Default implementation - subclasses should override
        raise NotImplementedError("Class must implement setup()")
        
    def teardown_context(self) -> None:
        """
        Teardown the context. Override this method in subclasses to provide custom cleanup.
        """
        # Default implementation - subclasses can override
        pass
        
    def __enter__(self):
        # Setup context - call the setup method to create/get the pyrosper instance
        self.pyrosper_instance = self.setup()

        # Store pyrosper instance
        self.instance_token = instance_storage.set(self.pyrosper_instance)
        
        return self.pyrosper_instance
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Teardown context
        self.teardown_context()
        
        # Reset context variables
        if self.instance_token is not None:
            instance_storage.reset(self.instance_token)

        return False

