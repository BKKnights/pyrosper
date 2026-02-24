from abc import ABC
from typing import Optional, TypeVar, Generic

ExperimentIdType = TypeVar('ExperimentIdType')
UserIdType = TypeVar('UserIdType')
UserVariantIdType = TypeVar('UserVariantIdType')

class UserVariant(ABC, Generic[ExperimentIdType, UserIdType, UserVariantIdType]):
  id: Optional["UserVariantIdType"]
  experiment_id: "ExperimentIdType"
  user_id: "UserIdType"
  index: int

  def __init__(self, experiment_id: "ExperimentIdType", index: int, user_id: "UserIdType", id: Optional["UserVariantIdType"] = None):
    self.id: Optional["UserVariantIdType"] = id
    self.experiment_id: "ExperimentIdType" = experiment_id
    self.user_id: "UserIdType" = user_id
    self.index: int = index
