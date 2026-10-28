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
from energy import get_loss_fraction





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
    
        self.supply_matrix = self._compute_required() #customer[i],  power_plant[j]
        self.initial = self._create_initial_state()


    def _create_initial_state(self, sol_type = 1) -> EnergyNetworkState:

        if sol_type == 0: #dels garantitzats, agafem assignem a la central primer més gran
            assignation = [None] * len(self.customers)

            sorted_customers = chain(
                (c[0] for c in enumerate(self.customers) if c[1].contract_type == 0),
                (c[0] for c in enumerate(self.customers) if c[1].contract_type == 1),
            )

            sorted_power_plants = sorted(range(len(self.power_plants)), 
                                         key= lambda plant_i: self.power_plants[plant_i].production_mw, 
                                         reverse=True)
            
            plants_available_energy = [plant.production_mw for plant in self.power_plants]

            for cust_i in sorted_customers:
                for plant_j in sorted_power_plants:
                    if self.supply_matrix[cust_i][plant_j] <= plants_available_energy[plant_j]:
                        assignation[cust_i] = plant_j
                        plants_available_energy[plant_j] -= self.supply_matrix[cust_i][plant_j]
                        break
                else:
                    if self.customers[cust_i].contract_type == 0:
                        print(f"lack of supply to guaranteed customer, No Valid solution")
                        return None


            return EnergyNetworkState(assignation, plants_available_energy)



    #     elif sol_type == 1: #dels garantitzats, agafem assignem a la central primer més propera
    #         #clients garantits --> ordre aleatori --> selecció només clients garantits
            # ordered = chain(
            #     (c for c in self.customers if c.contract_type == 0),
            #     (c for c in self.customers if c.contract_type == 1),
            # )

    #         #capacitat disponible inicial cada central
    #         remaining_capacity = [plant.production_mw for plant in self.power_plants]

            
            

        # return initial_state

    def ordering_pow_plant_distance_for_customer(self, customer): # retornem els índexs de lesc entrals ordenades per distància al client
        total_distances_customer = []

        for i, plant in enumerate(self.power_plants): 
            distance = hypot(customer.x - plant.x, customer.y - plant.y)

            total_distances_customer.append((distance, i ))

        return total_distances_customer.sort()


    def _compute_required(self):

        return [
            [customer.demand_mw/(1- get_loss_fraction(self._distance(customer, power_plant))) for power_plant in self.power_plants]
            for customer in self.customers
        ]
   
    def _distance(self, customer, plant):
        return hypot(customer.x - plant.x, customer.y - plant.y)


    def actions(self, state):
        pass

    def result(self, state, action):
        pass
        # return super().result(state, action)

    def value(self, state):
        pass
        # return super().value(state)

