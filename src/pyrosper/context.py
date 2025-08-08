import asyncio
from contextlib import ContextDecorator
from contextvars import ContextVar
from functools import wraps
from typing import Optional, Any
from .pyrosper import Pyrosper

context_storage = ContextVar("pyrosper_context_storage", default="unknown")
instance_storage = ContextVar("pyrosper_instance_storage", default=None)

def context():
    def decorator(func):
        # Generate context name from function type
        if asyncio.iscoroutinefunction(func):
            context_name = f"async_{func.__name__}"
        else:
            context_name = f"sync_{func.__name__}"

        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                token = context_storage.set(context_name)
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    raise e
                finally:
                    context_storage.reset(token)

            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                token = context_storage.set(context_name)
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    raise e
                finally:
                    context_storage.reset(token)

            return sync_wrapper

    return decorator


def get_current() -> 'Pyrosper':
    """Get the current pyrosper instance from context."""
    result: Optional['Pyrosper'] = instance_storage.get()
    if not result:
        raise RuntimeError("No pyrosper instance found in context")
    return result


class Context(ContextDecorator):
    """
    Context manager and decorator for Pyrosper context isolation.
    
    This class can be extended to provide custom context setup and teardown.
    It automatically handles context variable management and cleanup.
    
    Usage as context manager:
        with Context() as pyrosper:
            # Use pyrosper instance
            pass
    
    Usage as decorator:
        @Context()
        def my_function():
            pyrosper = get_current_pyrosper()
            # Use pyrosper instance
            pass
    """
    
    def __init__(self):
        self.token = None
        self.instance_token = None
        self.pyrosper_instance = None
        
    def setup_context(self) -> Any:
        """
        Setup the context. Override this method in subclasses to provide custom setup.
        
        Returns:
            The pyrosper instance to use in this context.
        """
        # Default implementation - subclasses should override
        raise NotImplementedError("Class must implement setup_context()")
        
    def teardown_context(self) -> None:
        """
        Teardown the context. Override this method in subclasses to provide custom cleanup.
        """
        # Default implementation - subclasses can override
        pass
        
    def __enter__(self):
        # Setup context - call the setup method to create/get the pyrosper instance
        self.pyrosper_instance = self.setup_context()
        
        # Store context name
        context_name = f"pyrosper_context_{id(self)}"
        self.token = context_storage.set(context_name)
        
        # Store pyrosper instance
        self.instance_token = instance_storage.set(self.pyrosper_instance)
        
        return self.pyrosper_instance
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Teardown context
        self.teardown_context()
        
        # Reset context variables
        if self.instance_token is not None:
            instance_storage.reset(self.instance_token)
        if self.token is not None:
            context_storage.reset(self.token)
            
        return False

