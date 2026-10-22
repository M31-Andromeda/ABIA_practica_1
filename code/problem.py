import random
import sys
from dataclasses import dataclass
from collections.abc import Sequence
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "given_code"))    

from aima.search import Problem, Node
from network_state import EnergyNetworkState
from customers import generate_customers
from power_plants import generate_power_plants


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

    
class EnergyNetworkProblem(Problem):
    def __init__(self, config: Params):

        self.config = config
        self.rand = random.Random(config.seed)
        self.power_plants = generate_power_plants(config.counts, config.seed)
        self.customers = generate_customers(config.count, config.type_proportions, config.guaranteed_proportion, config.seed)
        self.customers = sorted(self.customers, key=lambda c: (c.x, c.y)) 

        self.supply = self._compute_supply() 
        self.initial = self._create_initial_state()


    def _create_initial_state(self) -> EnergyNetworkState:

        return EnergyNetworkState()

    def _compute_supply(self) -> list[list[float]]:
        supply = []
        for plant in self.power_plants:
            for customer in self.customers:
                pass    


    def actions(self, state):
        pass

    def result(self, state, action):
        pass
        # return super().result(state, action)

    def value(self, state):
        pass
        # return super().value(state)

