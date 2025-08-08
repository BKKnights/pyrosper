from typing import Any, Dict, Union




class Variant:
    # also allow picks to be a class
    def __init__(self, name: str, picks: Union[Dict[object, Any], Any]):
        self.name = name
        self.picks = picks

    def get_pick(self, symbol: object) -> Any:
        return self.picks[symbol]

