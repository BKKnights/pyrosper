from typing import Any, Dict, TypeVar

T = TypeVar('T')

class Variant:
    def __init__(self, name: str, picks: Dict[object, Any]):
        self.name = name
        self.picks = picks

    def get_pick(self, symbol: object) -> T:
        return self.picks[symbol]