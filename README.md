# `\\//,` pyrosper (pronounced "prosper")

A continuously improving, experimentation framework for Python.
Ported from the [TypeScript counterpart](https://github.com/BKKnights/prosper).

## Installation

```bash
pip install pyrosper
```

Or install from source:

```bash
git clone https://github.com/your-repo/pyrosper.git
cd pyrosper
pip install -e .
```

## Why pyrosper?

pyrosper provides a means of:
* Injecting intelligently selected experimental code that is short-lived
* Using any algorythm of your choosing to select which experimental code is injected for a user
  * as simple as returning  index, like random
  * as sophisticated as a multi-armed bandit  
* Preventing code churn where long-lived code belongs

### The non-pyrosper way:
* Uses feature flagging
* Favors code churn, with highly fractured experimentation
* Constantly affects test coverage
* Provides a very blurry understanding of the codebase when experimenting

### The pyrosper way:
* Use experiments rather than feature flags
  * Picture one master switch, rather than many small switches
  * Code for each variant lives close together, within an experiment
* Favors short-lived experimental code that accentuates long-lived code
  * Once understandings from a variant are known, they can be moved from short-lived (experiment) to long-lived (source)
* Meant to churn as little as possible
* Provides a very clear understanding of the codebase when experimenting

## Quick Start

### Basic Usage

```python
from pyrosper import Pyrosper, Symbol, Variant, BaseExperiment
from typing import List

# Define your experiment
class MyExperiment(BaseExperiment):
    # Implement abstract methods (see full example below)
    async def get_experiment(self):
        # Your implementation here
        pass
    
    # ... other required methods

# Create and use pyrosper
pyrosper = Pyrosper()
key = Symbol("greeting")
experiment = MyExperiment(
    name="greeting_experiment",
    variants=[
        Variant("control", {key: "Hello!"}),
        Variant("variant_a", {key: "Hi there!"}),
        Variant("variant_b", {key: "Hey!"}),
    ]
)
pyrosper.with_experiment(experiment)

# Get a value from the experiment
greeting_symbol = Symbol("greeting")
greeting = pyrosper.pick(greeting_symbol)
print(greeting)  # Will print one of: "Hello!", "Hi there!", or "Hey!"
```

### Using the Context System

```python
from pyrosper import Context, get_current, context

# Create a custom context
class UserContext(Context):
    def __init__(self, user_id: str):
        super().__init__()
        self.user_id = user_id
    
    def setup_context(self):
        # Create and configure pyrosper for this user
        pyrosper = Pyrosper()
        # Add experiments, configure algorithms, etc.
        return pyrosper
key = Symbol("greeting")
# Use as context manager
with UserContext("user123") as pyrosper:
    current = get_current()  # Get current pyrosper instance
    greeting = current.pick(key)

# Use as decorator
@context()
def get_user_greeting():
    pyrosper = get_current()
    return pyrosper.pick(key)

result = get_user_greeting()
```

### Type-Safe Picking

```python
from pyrosper import pick

# Define your variant types
class GreetingVariant:
    def __init__(self, message: str, emoji: str):
        self.message = message
        self.emoji = emoji

# Create variants
control_variant = GreetingVariant("Hello", "👋")
variant_a = GreetingVariant("Hi there", "😊")
key = Symbol("greeting")
# Use type-safe picking
greeting = pick(pyrosper_instance, key, GreetingVariant) # `pick` is a helper function, not required
greeting = pyrosper_instance.pick(key, GreetingVariant) # usage with `pick` method
print(f"{greeting.message} {greeting.emoji}")
```

## Complete Example

Here's a complete example showing how to implement a real experiment:

```python
import asyncio
from typing import List, Optional
from pyrosper import Pyrosper, Symbol, Variant, BaseExperiment, UserVariant

# Define your data models
class UserVariantImpl(UserVariant):
    def __init__(self, experiment_id: str, user_id: str, index: int):
        self.experiment_id = experiment_id
        self.user_id = user_id
        self.index = index

class Algorithm:
    def __init__(self, weights: List[float]):
        self.weights = weights

# Implement your experiment
class GreetingExperiment(BaseExperiment):
    def __init__(self):
        super().__init__(
            name="greeting_experiment",
            variants=[
                Variant("control", {Symbol("greeting"): "Hello!"}),
                Variant("friendly", {Symbol("greeting"): "Hi there!"}),
                Variant("casual", {Symbol("greeting"): "Hey!"}),
            ]
        )
        self._algorithm = Algorithm([0.33, 0.33, 0.34])
        self._user_variants = {}
    
    async def get_experiment(self) -> Optional['GreetingExperiment']:
        return self if self.is_enabled else None
    
    async def upsert_experiment(self, experiment) -> 'GreetingExperiment':
        self.is_enabled = experiment.is_enabled
        self.id = experiment.id
        return self
    
    async def delete_experiment(self, experiment) -> None:
        self.reset()
    
    async def get_user_variant(self, user_id: str, experiment_id: str) -> Optional[UserVariantImpl]:
        return self._user_variants.get(f"{user_id}_{experiment_id}")
    
    async def upsert_user_variant(self, user_variant: UserVariantImpl) -> None:
        self._user_variants[f"{user_variant.user_id}_{user_variant.experiment_id}"] = user_variant
    
    async def delete_user_variant(self, user_variant: UserVariantImpl) -> None:
        key = f"{user_variant.user_id}_{user_variant.experiment_id}"
        if key in self._user_variants:
            del self._user_variants[key]
    
    async def delete_user_variants(self) -> None:
        self._user_variants.clear()
    
    async def get_algorithm(self) -> Algorithm:
        return self._algorithm
    
    async def get_variant_index(self, algorithm: Algorithm) -> int:
        # Simple random selection based on weights
        import random
        return random.choices(range(len(algorithm.weights)), weights=algorithm.weights)[0]
    
    async def reward_algorithm(self, algorithm: Algorithm, user_variant_index: int, score: float) -> Algorithm:
        # Update weights based on performance
        new_weights = algorithm.weights.copy()
        new_weights[user_variant_index] *= (1 + score * 0.1)
        # Normalize weights
        total = sum(new_weights)
        new_weights = [w / total for w in new_weights]
        return Algorithm(new_weights)
    
    async def upsert_algorithm(self, algorithm: Algorithm) -> None:
        self._algorithm = algorithm
    
    async def delete_algorithm(self) -> None:
        self._algorithm = Algorithm([0.33, 0.33, 0.34])

# Usage
async def main():
    # Create pyrosper instance
    pyrosper = Pyrosper()
    
    # Create and add experiment
    experiment = GreetingExperiment()
    pyrosper.with_experiment(experiment)
    
    # Enable the experiment
    await experiment.enable()
    
    # Set up for a specific user
    await pyrosper.set_for_user("user123")
    
    # Get greeting for user
    greeting_symbol = Symbol("greeting")
    greeting = pyrosper.pick(greeting_symbol, pick_type)
    print(f"Greeting for user123: {greeting}")
    
    # Complete experiment for user (provide feedback)
    await experiment.complete_for_user("user123", 0.8)  # 0.8 score

# Run the example
if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Features

### Multiple Experiments

```python
# Create multiple experiments
greeting_exp = GreetingExperiment()
color_exp = ColorExperiment()

# Add to pyrosper
pyrosper = Pyrosper()
pyrosper.with_experiment(greeting_exp).with_experiment(color_exp)

# Use both experiments
greeting = pyrosper.pick(Symbol("greeting"))
color = pyrosper.pick(Symbol("color"))
```

### Experiment Validation

Pyrosper automatically validates experiments to ensure:
- No duplicate experiment names
- All variants have the same symbols
- No duplicate symbols across experiments

```python
# This will raise ValueError if validation fails
pyrosper.with_experiment(experiment)
```

### Context Isolation

```python
# Each context has its own pyrosper instance
with UserContext("user1") as pyrosper1:
    with UserContext("user2") as pyrosper2:
        # pyrosper1 and pyrosper2 are independent
        greeting1 = pyrosper1.pick(Symbol("greeting"))
        greeting2 = pyrosper2.pick(Symbol("greeting"))
```

## API Reference

### Core Classes

- **`Pyrosper`**: Main class for managing experiments
- **`BaseExperiment`**: Abstract base class for experiments
- **`Variant`**: Represents a single variant in an experiment
- **`Symbol`**: Unique identifier for experiment values
- **`Context`**: Context manager for pyrosper instances

### Key Methods

#### Pyrosper
- `with_experiment(experiment)`: Add an experiment
- `pick(symbol)`: Get a value from experiments
- `has_pick(symbol)`: Check if symbol exists
- `set_for_user(user_id)`: Set up experiments for a user

#### BaseExperiment
- `enable()`: Enable the experiment
- `disable()`: Disable the experiment
- `complete_for_user(user_id, score)`: Provide feedback
- `get_variant(user_id)`: Get the variant for a user

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT

---

Vulcans are cool. 🖖
