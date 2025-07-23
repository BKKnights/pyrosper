## `\\//,` pyrosper (pronounced "prosper")
A continuously improving, experimentation framework. Now in python.

### Installation
TBD

### Why
pyrosper provides a means of:
* injecting intelligently selected experimental code that is shorted lived
* using multi armed bandit machine learning to selected which experimental code is injected
* prevents code churn where long-lived code belongs

The non-pyrosper way:
* Uses feature flagging
* Favors code churn, with highly fractured experimentation
* Constantly effects test coverage
* Provides a very blurry understanding of the code base when experimenting

The pyrosper way:
* Use experiments rather than Features Flags
  * Picture one master switch, rather than a many small switches
  * Code for each variant lives close together, within an experiment
* Favors short-lived experimental code, that accentuates long-lived code
  * Once understandings from a variant is known, then it can be moved from short-lived (experiment) to long-lived (source)
* Meant to churn as little as possible.
* Provides a very clear understanding of the code base when experimenting


### Examples
TBD

...Vulcan's are cool.
