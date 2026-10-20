
from aima.search import Problem, Node, astar_search
from network_state import EnergyNetworkState
from dataclasses import dataclass
from collections.abc import Sequence
from given_code.customers import generate_customers
from given_code.power_plants import generate_power_plants

import random

class EnergyNetworkProblem(Problem):
    def __init__(self, config: Params):

        self.config = config
        self.rand = random.Random(config.seed)
        self.power_plants = generate_power_plants(config.counts, config.seed)
        self.customers = generate_customers(config.count, config.type_proportions, config.guaranteed_proportion, config.seed)
        self.initial = self._create_initial_state()


    def _create_initial_state(self) -> EnergyNetworkState:


        return EnergyNetworkState()


    def actions(self, state):
        pass

    def result(self, state, action):
        pass
        # return super().result(state, action)

    def value(self, state):
        pass
        # return super().value(state)


@dataclass
class Params:

    seed: int = 69

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

    

