from problem import EnergyNetworkProblem
from operators import Move, Swap


class EnergyNetworkProblemSA(EnergyNetworkProblem):
    """
    Problema per a Simulated Annealing: hereta tot d'EnergyNetworkProblem (matrius, solució inicial,
    result() i value()) i només canvia actions(): en lloc de generar tots els successors,
    tria un operador a l'atzar i uns paràmetres a l'atzar i retorna UNA sola acció vàlida.

    Ús:
        from aima.search import simulated_annealing, exp_schedule
        problem = EnergyNetworkProblemSA(config, operators, sol_type)
        solution = simulated_annealing(problem, exp_schedule(k, lam, limit))
    """

    MAX_TRIES = 1000 #intents per trobar una acció vàlida abans de rendir-se

    def actions(self, state):
        #IMPORTANT: si es retorna una llista buida, simulated_annealing s'atura i retorna l'estat actual
        for _ in range(self.MAX_TRIES):
            operator = self.rand.choice(self.operators) #self.rand ja està inicialitzat amb la seed a l'__init__

            if operator is Move:
                action = self._random_move(state)
            else:
                action = self._random_swap(state)

            if action is not None:
                return [action]

        return []


    def _random_move(self, state):
        #retorna un Move vàlid triat a l'atzar, o None si el que ha sortit no és vàlid (actions() tornarà a provar)

        cust_i = self.rand.randrange(len(self.customers))
        customer = self.customers[cust_i]
        plant_desti = self.rand.choice(list(range(len(self.power_plants))) + [None])
        on_plant_i = state.network[cust_i]

        #el destí és la mateixa central on ja està
        if on_plant_i == plant_desti:
            return None
        #el destí és None però el client és garantit, o no està servit
        if plant_desti == None and (customer.contract_type == 0 or on_plant_i is None):
            return None
        #el destí és una central on no hi cap (mateixa condició que a actions() d'EnergyNetworkProblem)
        if plant_desti is not None and  self.supply_matrix[cust_i][plant_desti] > state.plants_available_energy[plant_desti]:
            return None
        
        return Move(cust_i, on_plant_i, plant_desti)


    def _random_swap(self, state):
        #retorna un Swap vàlid triat a l'atzar, o None si el que ha sortit no és vàlid
        cust_i, cust_j = self.rand.randrange(len(self.customers)), self.rand.randrange(len(self.customers))
        customer_1, 


















        # TODO 1: tria dos clients diferents a l'atzar -> cust_i, cust_j

        # TODO 2: descarta (return None) si algun no està servit o si estan a la mateixa central

        # TODO 3: comprova que hi caben després d'intercanviar-los (mateixa condició que a actions() d'EnergyNetworkProblem)

        # TODO 4: return Swap(cust_i, cust_j)
        return None
