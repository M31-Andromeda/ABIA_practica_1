import random
import sys
import heapq
from math import hypot #distància euclidiana (per a totes les centrals)
from dataclasses import dataclass
from collections.abc import Sequence
from pathlib import Path
from itertools import chain, groupby
from aima.search import Problem, Node

sys.path.insert(0, str(Path(__file__).parent.parent / "given_code"))    
from customers import generate_customers
from power_plants import generate_power_plants
from energy import get_loss_fraction
from network_state import EnergyNetworkState






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

        if sol_type == 0: #per ordre de prioritat, assignem a les centrals amb més producció
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
                for plant_i in sorted_power_plants:
                    if self.supply_matrix[cust_i][plant_i] <= plants_available_energy[plant_i]:
                        assignation[cust_i] = plant_i
                        plants_available_energy[plant_i] -= self.supply_matrix[cust_i][plant_i]
                        break
                else:
                    if self.customers[cust_i].contract_type == 0:
                        print(f"lack of supply to guaranteed customer, No Valid solution")
                        return None


            return EnergyNetworkState(assignation, plants_available_energy)



        elif sol_type == 1: #de tots el clients, amb prioritat, li seleccionem qualsevol central que tingui cost mínim per ell.
            assignation = [None] * len(self.customers)

            sorted_customers = chain(
                (c[0] for c in enumerate(self.customers) if c[1].contract_type == 0),
                (c[0] for c in enumerate(self.customers) if c[1].contract_type == 1),
            )

            plants_available_energy = [plant.production_mw for plant in self.power_plants]

            for cust_i in sorted_customers:
                plant_cost_lst = sorted(enumerate(self.supply_matrix[cust_i]), key = lambda x:x[1])
                for plant_i, plant_cost in plant_cost_lst:
                    if plants_available_energy[plant_i] >= plant_cost:
                        assignation[cust_i] = plant_i
                        plants_available_energy[plant_i] -= plant_cost
                        break

                else:
                    if self.customers[cust_i].contract_type == 0:
                        print(f"lack of supply to guaranteed customer, No Valid solution")
                        return None

            return EnergyNetworkState(assignation, plants_available_energy)


        elif sol_type == 2: #de tots el clients, amb prioritat, els hi seleccionem les centrals amb le mateix coste de suplir i per desempatara, escollim primer les que estan enceces y despres les mes grans
            assignation = [None] * len(self.customers)

            sorted_customers = chain(
                (c[0] for c in enumerate(self.customers) if c[1].contract_type == 0),
                (c[0] for c in enumerate(self.customers) if c[1].contract_type == 1),
            )

            plants_available_energy = [plant.production_mw for plant in self.power_plants]

            for cust_i in sorted_customers:
                best_candidate_index = None #power_plant index
                best_candidate = None #same plant of above, but in a tuple, with useful data to compare

                for plant_i, plant_cost in enumerate(self.supply_matrix[cust_i]):
                    plant = self.power_plants[plant_i]

                    if plants_available_energy[plant_i] < plant_cost:
                        continue

                    candidate = (-plant_cost, plants_available_energy[plant_i] < plant.production_mw, plant.production_mw) #tuple -cost, True if power_plant is on, else False, and size of the plant
                    if best_candidate_index is None:
                        best_candidate_index = plant_i
                        best_candidate = candidate
                    elif candidate > best_candidate: #compara dos tuples de l'estil (-2.3, True, 500) on el primer és el -cost, el segon element és si esta encessa, i el tercer que tan gran es la central
                        best_candidate_index = plant_i
                        best_candidate = candidate
                    
                if best_candidate_index is not None:
                    assignation[cust_i] = best_candidate_index
                    plants_available_energy[best_candidate_index] -= self.supply_matrix[cust_i][best_candidate_index]
                    

                elif self.customers[cust_i].contract_type == 0:
                    print(f"lack of supply to guaranteed customer, No Valid solution")
                    return None

            return EnergyNetworkState(assignation, plants_available_energy)
         
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

