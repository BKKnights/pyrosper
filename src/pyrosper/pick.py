from typing import TypeVar, Generic, Type, overload, Any, Callable

from pyrosper import Symbol

T = TypeVar("T")

class Pick(Generic[T]):
    typ: Type[T]
    symbol: Symbol
    getter: Callable[[], T]

    def __init__(self, typ: Type[T], symbol: Symbol, getter: Callable[[], T]):
        self.typ = typ
        self.symbol = symbol
        self.getter = getter

    def __set_name__(self, owner, name):
        pass

    @overload
    def __get__(self, instance: None, owner: Any) -> "Pick[T]":
        ...

    @overload
    def __get__(self, instance: Any, owner: Any) -> T:
        ...

    def __get__(self, instance, owner):
        if instance is None:
            return self
        result = self.getter()
        if not isinstance(result, self.typ):
            raise TypeError(f"Expected {self.typ}, got {type(result)}")
        return result


    def __set__(self, instance, value: T):
        raise AttributeError("Cannot set property")