import random
from aima.search import Problem

from given import (
    generate_customers,
    generate_power_plants,
    get_guaranteed_tariff,
    get_non_guaranteed_tariff,
    get_non_service_penalty,
    get_production_cost_per_mw,
    get_running_cost,
    get_stopped_cost,
)
import pre_processing as pre
from network_state import EnergyNetworkState
from operators import Move, Swap
from parameters import Params
from state_initializer import get_initial_config


    
class EnergyNetworkProblem(Problem):
    def __init__(self, config: Params):

        self.config = config
        self.rand = random.Random(config.seed)
        self.operators = config.operators
        self.power_plants = generate_power_plants(config.counts, config.seed)
        self.customers = generate_customers(config.count, config.type_proportions, config.guaranteed_proportion, config.seed)
        self.w1 = config.weights[0]
        self.guaranteed_penalty = config.guaranteed_penalty #experiment 5
    
        self.supply_matrix = pre.compute_supply_mat(self.customers, self.power_plants) #customer[i],  power_plant[j]
        self.loss_matrix = pre.compute_loss(self.customers, self.supply_matrix) #customer[i],  power_plant[j]
        self.customer_gain = pre.compute_customer_gain(self.customers, self.guaranteed_penalty) #customer[i]
        self.plant_switch_cost = pre.compute_switch_cost(self.power_plants) #power_plant[j]
        self.initial = self._create_initial_state(config.ini_sol_type)


    def _create_initial_state(self, ini_sol_type = 1) -> EnergyNetworkState:
        assignation, plants_available_energy = get_initial_config(ini_sol_type, self.customers, self.power_plants, self.supply_matrix)
        if not assignation or not plants_available_energy:
            return None

        initial_state = EnergyNetworkState(assignation, plants_available_energy)
        self.value(initial_state)
        return initial_state
         

    def actions(self, state):
        available_actions = list()
        use_move = Move in self.operators
        use_swap = Swap in self.operators

        for cust_i, on_plant_i in enumerate(state.network):
            customer = self.customers[cust_i]
            if use_move:
                # MOVE: assignar o canviar de central
                for plant_j in range(len(self.power_plants)):
                    if plant_j == on_plant_i:
                        continue

                    if(self.supply_matrix[cust_i][plant_j] <= state.plants_available_energy[plant_j]):
                        available_actions.append(Move(cust_i, on_plant_i, plant_j))

                # MOVE: desassignar si està servit i no és garantit (o, a l'experiment 5, si hi ha penalització per als garantits)
                if on_plant_i is not None and (customer.contract_type == 1 or self.guaranteed_penalty is not None):
                    available_actions.append(Move(cust_i,on_plant_i, None))

            # SWAP
            if on_plant_i is not None and use_swap:
                for cust_j in range(cust_i + 1, len(state.network)):
                    on_plant_j = state.network[cust_j]
                    if on_plant_j is None or on_plant_j == on_plant_i:
                        continue

                    available_i = (state.plants_available_energy[on_plant_i] + self.supply_matrix[cust_i][on_plant_i])
                    available_j = (state.plants_available_energy[on_plant_j] + self.supply_matrix[cust_j][on_plant_j])

                    if self.supply_matrix[cust_j][on_plant_i] <= available_i and self.supply_matrix[cust_i][on_plant_j] <= available_j:
                        available_actions.append(Swap(cust_i, cust_j)) 

        return available_actions
        


    def result(self, state, action):
        new_value_list = [state.value]
        network = list(state.network)
        plants_available_energy = list(state.plants_available_energy)

        if isinstance(action, Move):
            cust_i = action.cust_i
            plant_ori, plant_desti = action.orig, action.desti
            network[cust_i] = plant_desti

            # treure el client de la central d'origen (si en tenia)
            if plant_ori is not None:
                plants_available_energy[plant_ori] += self.supply_matrix[cust_i][plant_ori]
                new_value_list.append(-self.customer_gain[cust_i])
                new_value_list.append(self.w1*self.loss_matrix[cust_i][plant_ori])
                if self._plant_is_empty(plants_available_energy, plant_ori): # s'ha quedat sense clients -> s'apaga
                    new_value_list.append(self.plant_switch_cost[plant_ori])

            # posar el client a la central de destí (si en té)
            if plant_desti is not None:
                if self._plant_is_empty(plants_available_energy, plant_desti): # no tenia clients -> s'encén
                    new_value_list.append(-self.plant_switch_cost[plant_desti])
                plants_available_energy[plant_desti] -= self.supply_matrix[cust_i][plant_desti]
                new_value_list.append(self.customer_gain[cust_i])
                new_value_list.append(-self.w1*self.loss_matrix[cust_i][plant_desti])

        if isinstance(action, Swap):
            cust_i, cust_j = action.cust_i, action.cust_j
            plant_i, plant_j = network[cust_i], network[cust_j]

            plants_available_energy[plant_i] += self.supply_matrix[cust_i][plant_i] - self.supply_matrix[cust_j][plant_i]
            plants_available_energy[plant_j] += self.supply_matrix[cust_j][plant_j] - self.supply_matrix[cust_i][plant_j]

            network[cust_i], network[cust_j] = plant_j, plant_i

            # cap central s'encén ni s'apaga i els dos clients segueixen servits: només canvien les pèrdues
            new_value_list.extend([
                self.w1*self.loss_matrix[cust_i][plant_i], self.w1*self.loss_matrix[cust_j][plant_j],
                -self.w1*self.loss_matrix[cust_i][plant_j], -self.w1*self.loss_matrix[cust_j][plant_i],
            ])


        new_state = EnergyNetworkState(network, plants_available_energy)
        new_state.value = sum(new_value_list)
        return new_state


    def goal_test(self, state):
        #cerca local: no podem saber si hem arribat a l'estat final, per tant sempre fals
        return False


    def value(self, state):
        if state.value is None:
            transactions = list()
            plant_on = [False] * len(self.power_plants)

            for cust_i, plant_i in enumerate(state.network):
                customer = self.customers[cust_i]
                if plant_i is None:
                    transactions.append(-1*get_non_service_penalty(customer.customer_type)*customer.demand_mw)
                    if customer.contract_type == 0 and self.guaranteed_penalty is not None:  #experiment 5
                        transactions.append(-1*self.guaranteed_penalty*customer.demand_mw)
                else:
                    plant_on[plant_i] = True
                    if customer.contract_type == 0: # GUARANTEED
                        transactions.append(get_guaranteed_tariff(customer.customer_type)*customer.demand_mw)

                    elif customer.contract_type == 1: # NOT GUARANTEED
                        transactions.append(get_non_guaranteed_tariff(customer.customer_type)*customer.demand_mw)

                    #penalitza els MW perduts en el transport, que creixen per trams amb la distància i amb la demanda del client
                    transactions.append(-self.w1*(self.supply_matrix[cust_i][plant_i] - customer.demand_mw))


            #les centrals enceses paguen el cost fix més el de tota la producció, i les apagades el cost fix de parada
            for plant_i, plant in enumerate(self.power_plants):
                if plant_on[plant_i]:
                    transactions.append(-1*(get_running_cost(plant.plant_type) + get_production_cost_per_mw(plant.plant_type)* plant.production_mw))
                else: 
                    transactions.append(-1*get_stopped_cost(plant.plant_type))
            
            state.value = sum(transactions)

        return state.value


    def _plant_is_empty(self, plants_available_energy, plant_i):
        #si no té clients, l'energia lliure és tota la producció (cada client gasta >= 1 MW, la tolerància només absorbeix errors de float)
        return plants_available_energy[plant_i] >= self.power_plants[plant_i].production_mw - 1e-6

