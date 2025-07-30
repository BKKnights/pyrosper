from typing import Any, Dict

class Variant:
    def __init__(self, name: str, picks: Dict[object, Any]):
        self.name = name
        self.picks = picks

    def get_pick(self, symbol: object) -> Any:
        return self.picks[symbol]