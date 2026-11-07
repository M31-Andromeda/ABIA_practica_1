from math import hypot

from given import (
    get_guaranteed_tariff,
    get_non_guaranteed_tariff,
    get_non_service_penalty,
    get_production_cost_per_mw,
    get_running_cost,
    get_stopped_cost,
    get_loss_fraction,
)


def compute_supply_mat(customers, power_plants):

    return [
        [customer.demand_mw/(1- get_loss_fraction(_distance(customer, power_plant))) for power_plant in power_plants]
        for customer in customers
    ]

def compute_loss(customers, supply_matrix):
    #MW perduts en el transport si la central j serveix el client i (el pes w1 s'aplica a value() i result())
    return [
        [supply - customer.demand_mw for supply in supply_matrix[cust_i]]
        for cust_i, customer in enumerate(customers)
    ]

def compute_customer_gain(customers, guaranteed_penalty = None):
    #el que guanya el valor quan un client passa de no servit a servit: cobrem la tarifa i deixem de pagar la indemnització
    gains = list()
    for customer in customers:
        if customer.contract_type == 0: # GUARANTED
            tariff = get_guaranteed_tariff(customer.customer_type)
            if guaranteed_penalty is not None:  #experiment 5
                tariff += guaranteed_penalty
        else: # NOT GUARANTED
            tariff = get_non_guaranteed_tariff(customer.customer_type)
        gains.append((tariff + get_non_service_penalty(customer.customer_type))*customer.demand_mw)
    return gains

def compute_switch_cost(power_plants):
    #el que costa de més tenir la central encesa respecte a tenir-la parada
    return [
        get_running_cost(plant.plant_type) + get_production_cost_per_mw(plant.plant_type)*plant.production_mw - get_stopped_cost(plant.plant_type)
        for plant in power_plants
    ]

def _distance(customer, plant):
    return hypot(customer.x - plant.x, customer.y - plant.y)

