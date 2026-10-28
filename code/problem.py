import random
import sys
import heapq
from math import hypot #distància euclidiana (per a totes les centrals)
from dataclasses import dataclass
from collections.abc import Sequence
from pathlib import Path
from itertools import chain
from aima.search import Problem, Node
from network_state import EnergyNetworkState

sys.path.insert(0, str(Path(__file__).parent.parent / "given_code"))    
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

        self.supply = self._compute_supply() 
        self.initial = self._create_initial_state()


    def _create_initial_state(self, type = 0) -> EnergyNetworkState:
        initial_state = EnergyNetworkState(self.customers)

        if type == 0: #dels garantitzats, agafem aleatoriament i assignem a la central primer més gran

            customers_copy = self.customers.copy()
            self.rand.shuffle(customers_copy)
            ordered = chain(
                (c for c in customers_copy if c.contract_type == 0),
                (c for c in customers_copy if c.contract_type == 1),
            )

            sorted_production_plants = sorted(self.power_plants, key= lambda plant: plant.production_mw, reverse=True)
            production_x_plant = zip([plant.production_mw for plant in sorted_production_plants], sorted_production_plants)

            for customer in ordered:
                for index, (production, plant) in enumerate(production_x_plant):
                    if customer.demand_mw <= production:
                        initial_state.set_customer_to_plant(customer, plant)
                        production_x_plant[index][0] -= customer.demand_mw
                        break






        elif type == 1: #dels garantitzats, agafem aleatoriament i assignem a la central primer més propera
            #clients garantits --> ordre aleatori --> selecció només clients garantits
            customers_copy = self.customers.copy()
            self.rand.shuffle(customers_copy)
            ordered = chain(
                            (c for c in customers_copy if c.contract_type == 0),
                            (c for c in customers_copy if c.contract_type == 1),
                        )

            #capacitat disponible inicial cada central
            remaining_capacity = [plant.production_mw for plant in self.power_plants]

            
            

        return initial_state

    def ordering_pow_plant_distance_for_customer(self, customer): # retornem els índexs de lesc entrals ordenades per distància al client
        total_distances_customer = []

        for i, plant in enumerate(self.power_plants): 
            distance = hypot (customer.x - plant.x, customer.y - plant.y)

            total_distances_customer.append((distance, i ))

        return total_distances_customer.sort()


    def _compute_supply(self):
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

