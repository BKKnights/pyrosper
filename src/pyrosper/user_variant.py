from typing import Optional

class UserVariant:
  id: Optional[str]
  experiment_id: str
  user_id: str
  index: int

  def __init__(self, experiment_id: str, index: int, user_id: str, id: Optional[str] = None):
    self.id: Optional[str] = id
    self.experiment_id: str = experiment_id
    self.user_id: str = user_id
    self.index: int = index
