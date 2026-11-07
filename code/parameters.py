from collections.abc import Sequence
from dataclasses import dataclass

@dataclass
class Params:

    seed: int

    #----power_plants----#
    counts: Sequence[int]
    """Three non-negative counts to create power plants of types A, B and C."""

    #----customers----#
    count: int
    """Non-negative number of customers to generate."""

    type_proportions: Sequence[float]
    """Three probabilities, summing to one, for extra-large, very large and large customers, respectively."""

    guaranteed_proportion: float
    """Probability of a guaranteed contract, in [0, 1]."""

    weights: Sequence[float]
    """weights for the evaluation function"""

