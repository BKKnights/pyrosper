class Symbol:
    def __init__(self, description: str):
        self.description = description
        self.unique_id = id(self)

    def __repr__(self):
        return f"Symbol({self.description})"