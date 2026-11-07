from itertools import chain

def _no_valid_solution():
    print(f"lack of supply to guaranteed customer, No Valid solution")
    return None, None

def get_initial_config(ini_sol_type, customers, power_plants, supply_matrix):

    #comú a totes les estratègies: cap client assignat, totes les centrals amb tota la producció lliure,
    #i es recorren primer els clients garantits i després els no garantits
    assignation = [None] * len(customers)

    sorted_customers = chain(
        (c[0] for c in enumerate(customers) if c[1].contract_type == 0),
        (c[0] for c in enumerate(customers) if c[1].contract_type == 1),
    )

    plants_available_energy = [plant.production_mw for plant in power_plants]


    if ini_sol_type == 0: #per ordre de prioritat, assignem a les centrals amb més producció
        sorted_power_plants = sorted(range(len(power_plants)),
                                        key= lambda plant_i: power_plants[plant_i].production_mw,
                                        reverse=True)

        for cust_i in sorted_customers:
            for plant_i in sorted_power_plants:
                if supply_matrix[cust_i][plant_i] <= plants_available_energy[plant_i]:
                    assignation[cust_i] = plant_i
                    plants_available_energy[plant_i] -= supply_matrix[cust_i][plant_i]
                    break
            else:
                if customers[cust_i].contract_type == 0:
                    return _no_valid_solution()


    elif ini_sol_type == 1: #de tots el clients, amb prioritat, li seleccionem qualsevol central que tingui cost mínim per ell.
        for cust_i in sorted_customers:
            plant_cost_lst = sorted(enumerate(supply_matrix[cust_i]), key = lambda x:x[1])
            for plant_i, plant_cost in plant_cost_lst:
                if plants_available_energy[plant_i] >= plant_cost:
                    assignation[cust_i] = plant_i
                    plants_available_energy[plant_i] -= plant_cost
                    break

            else:
                if customers[cust_i].contract_type == 0:
                    return _no_valid_solution()



    elif ini_sol_type == 2: #de tots el clients, amb prioritat, els hi seleccionem les centrals amb le mateix coste de suplir i per desempatara, escollim primer les que estan enceces y despres les mes grans
        for cust_i in sorted_customers:
            best_candidate_index = None #power_plant index
            best_candidate = None #same plant of above, but in a tuple, with useful data to compare

            for plant_i, plant_cost in enumerate(supply_matrix[cust_i]):
                plant = power_plants[plant_i]

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
                plants_available_energy[best_candidate_index] -= supply_matrix[cust_i][best_candidate_index]


            elif customers[cust_i].contract_type == 0:
                return _no_valid_solution()

    elif ini_sol_type == 3: #Experiment 5: Solució buida
        pass

    return assignation, plants_available_energy
