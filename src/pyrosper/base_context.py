from abc import ABC, abstractmethod, ABCMeta
from contextlib import ContextDecorator
from contextvars import ContextVar
from typing import Optional, Generic, TypeVar, Type

from . import Symbol
from .pick import Pick
from .pyrosper import Pyrosper

PyrosperType = TypeVar('PyrosperType', bound='Pyrosper')

class BaseMetaContext(ABCMeta, ContextDecorator, Generic[PyrosperType]):
    """
    Metaclass for BaseContext.
    """
    typed_instance_storage: ContextVar[Optional[PyrosperType]] = ContextVar("pyrosper_typed_instance_storage", default=None)

T = TypeVar("T")

class BaseContext(ABC, ContextDecorator, Generic[PyrosperType], metaclass=BaseMetaContext):
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
            pyrosper = get_current()
            # Use pyrosper instance
            pass
    """

    def __repr__(self):
        """Return a string representation of the context."""
        return f"{self.__class__.__name__}()"
    
    def __init__(self):
        """Initialize the context."""
        self.instance_token = None
        self.pyrosper_instance: Optional[PyrosperType] = None

    @abstractmethod
    def setup(self) -> PyrosperType:
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
        
    def __enter__(self) -> PyrosperType:
        # Setup context - call the setup method to create/get the pyrosper instance
        self.pyrosper_instance = self.setup()

        # Store pyrosper instance
        self.instance_token = self.__class__.typed_instance_storage.set(self.pyrosper_instance)
        
        return self.pyrosper_instance
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Teardown context
        self.teardown_context()
        
        # Reset context variables
        if self.instance_token is not None:
            self.__class__.typed_instance_storage.reset(self.instance_token)

        return False


    @classmethod
    def get_current(cls) -> PyrosperType:
        """Get the current pyrosper instance from context."""
        # Use cast to satisfy pytype if needed, or just type hint result.
        # But pytype seems to lose track of PyrosperType in the class scope for methods.
        result: Optional[PyrosperType] = cls.typed_instance_storage.get()
        if not result:
            raise RuntimeError("No pyrosper instance found in context")
        return result # pytype: disable=bad-return-type

    @classmethod
    def pick(cls, typ: Type[T], symbol: Symbol) -> Pick[T]:
        """
        Get a pick from the current pyrosper instance.
        """
        return Pick(typ, symbol, lambda: cls.get_current().pick(symbol, typ))
