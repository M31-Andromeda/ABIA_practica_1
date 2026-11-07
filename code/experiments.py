from aima.search import hill_climbing, simulated_annealing, InstrumentedProblem, exp_schedule
from operators import Move, Swap
import time
from statistics import mean
import random 
from dataclasses import replace

from network_state import EnergyNetworkState
from problem import EnergyNetworkProblem
from problem_sa import EnergyNetworkProblemSA
from parameters import Params

escenaris = [Params(seed=seed, 
                    counts=[5, 10, 25], 
                    count=1000,
                    type_proportions=[0.25, 0.30, 0.45], 
                    guaranteed_proportion=0.75, 
                    weights=[0.01],
                    operators=(Move, Swap),
                    ini_sol_type=1,
                    guaranteed_penalty=None)
                    for seed in range(10)]


def profit_and_losses(problem, state):
    #benefici real (€) i MW perduts: la heurística és h = benefici - w1 * MW perduts - càstig * MW garantits sense servir (exp 5)
    lost_mw = sum(problem.loss_matrix[c][p] for c, p in enumerate(state.network) if p is not None)
    unserved_mw = sum(problem.customers[c].demand_mw for c, p in enumerate(state.network)
                      if p is None and problem.customers[c].contract_type == 0)
    penalty = problem.guaranteed_penalty or 0
    return problem.value(state) + problem.w1 * lost_mw + penalty * unserved_mw, lost_mw



# EXP 1: Move sol o Move + Swap, quin va millor? (Hill Climbing)
def experiment_1():
    for operators in ((Move,), (Move, Swap)):
        values, profits, losses, durations, steps, neighbors = [], [], [], [], [], []

        for params in escenaris:
            e = EnergyNetworkProblem(replace(params, operators=operators))
            random.seed(params.seed)
            ip = InstrumentedProblem(e)
            start = time.perf_counter()
            solution = hill_climbing(ip)
            duration = time.perf_counter() - start

            value = e.value(solution)
            profit, lost_mw = profit_and_losses(e, solution)
            values.append(value)
            profits.append(profit)
            losses.append(lost_mw)
            durations.append(duration)
            steps.append(ip.succs - 1)
            neighbors.append(ip.states)
            #print(f"Operators: {operators}, Seed: {params.seed}, Value: {value}, Duration: {duration:.4f}s")

        print(f"Operators: {[op.__name__ for op in operators]}, Avg Value: {mean(values):.2f}, Avg Profit: {mean(profits):.2f} €, "
              f"Avg Lost: {mean(losses):.2f} MW, Avg Duration: {mean(durations):.4f}s, "
              f"Avg Steps: {mean(steps):.2f}, Avg Neighbors: {mean(neighbors):.2f}")
            
            

# EXP 2: Quina solució inicial és millor? (Hill Climbing)
def experiment_2():
    for ini_sol_type in (0,1,2):
        values, profits, losses, durations, steps, neighbors = [], [], [], [], [], []

        for params in escenaris:
            e = EnergyNetworkProblem(replace(params, ini_sol_type=ini_sol_type))
            if e.initial is None:
                continue

            ip = InstrumentedProblem(e)

            random.seed(params.seed)
            start = time.perf_counter()
            solution = hill_climbing(ip)
            duration = time.perf_counter() - start

            value = e.value(solution)
            profit, lost_mw = profit_and_losses(e, solution)
            values.append(value)
            profits.append(profit)
            losses.append(lost_mw)
            durations.append(duration)
            steps.append(ip.succs - 1)          # d'actions (i restem 1 per l'estat final que no el volem comptar)
            neighbors.append(ip.states)         # de result

        if not values:
            print(f"Initial Solution: {ini_sol_type}, cap solució inicial vàlida")
            continue

        print(f"Initial Solution: {ini_sol_type}, valid: {len(values)}/{len(escenaris)}, Avg Value: {mean(values):.2f}, "
              f"Avg Profit: {mean(profits):.2f} €, Avg Lost: {mean(losses):.2f} MW, Avg Duration: {mean(durations):.4f}s, "
              f"Avg Steps: {mean(steps):.2f}, Avg Neighbors: {mean(neighbors):.2f}")
            

# EXP 3: Quins paràmetres de Simulated Annealing són millors? 
def experiment_3():
    configuracions = (        # valors extrems pel SA
        (1, 0.01, 3000),      # Temperatura molt baixa, refredament ràpid
        (1000, 0.1, 3000),    # Temperatura alta, refredament ràpid
        (1, 0.0001, 3000),    # Temperatura baixa, refredament lent
        (1000, 0.0001, 3000), # Temperatura alta, refredament lent
    )

    for temperatura_inicial, refredament, max_iterations in configuracions:
        values, profits, losses, durations, iterations, neighbors = [], [], [], [], [], []

        for params in escenaris:
            e = EnergyNetworkProblemSA(params)
            random.seed(params.seed)

            ip = InstrumentedProblem(e)

            schedule = exp_schedule(k=temperatura_inicial, lam=refredament, limit=max_iterations)

            start = time.perf_counter()
            solution = simulated_annealing(ip, schedule)
            duration = time.perf_counter() - start

            value = e.value(solution)
            profit, lost_mw = profit_and_losses(e, solution)
            values.append(value)
            profits.append(profit)
            losses.append(lost_mw)
            durations.append(duration)
            iterations.append(ip.succs) # aquí mesurem les expansions no els moviments acceptats
            neighbors.append(ip.states)

        print(f"Initial solution: {params.ini_sol_type}, Temperature: {temperatura_inicial}, Cooling: {refredament}, "
              f"Limit: {max_iterations}, Mean h: {mean(values):.2f}, Avg Profit: {mean(profits):.2f} €, "
              f"Avg Lost: {mean(losses):.2f} MW, Mean Duration: {mean(durations):.4f}s, "
              f"Avg Steps: {mean(iterations):.2f}, Avg Neighbors: {mean(neighbors):.2f}")



# EXP 4: Com creix el temps d'execució amb el nombre de clients o centrals? (Hill Climbing)
def experiment_4():
    configuracions = (
        (250, (5, 10, 25)),
        (500, (5, 10, 25)),
        (750, (5, 10, 25)),
        (1000, (5, 10, 25)),
        (1000, (10, 20, 50)),
        (1000, (15, 30, 75)),
        (1000, (20, 40, 100)),
    )

    for nombre_clients, centrals_per_tipus in configuracions:
        values, profits, losses, durations, steps, neighbors = [], [], [], [], [], []

        for params in escenaris:
            e = EnergyNetworkProblem(replace(params, count=nombre_clients, counts=list(centrals_per_tipus)))

            if e.initial is None:
                continue

            ip = InstrumentedProblem(e)

            random.seed(params.seed)
            start = time.perf_counter()
            solution = hill_climbing(ip)
            duration = time.perf_counter() - start

            value = e.value(solution)
            profit, lost_mw = profit_and_losses(e, solution)
            values.append(value)
            profits.append(profit)
            losses.append(lost_mw)
            durations.append(duration)
            steps.append(ip.succs - 1)
            neighbors.append(ip.states)

        if not values:
            print(f"Clients: {nombre_clients}, Centrals: {sum(centrals_per_tipus)}{centrals_per_tipus}, cap solució inicial vàlida")
            continue

        print(f"Clients: {nombre_clients}, Centrals: {sum(centrals_per_tipus)}{centrals_per_tipus}, Valid: {len(values)}/{len(escenaris)}, "
              f"Avg Value: {mean(values):.2f}, Avg Profit: {mean(profits):.2f} €, Avg Lost: {mean(losses):.2f} MW, "
              f"Avg Duration: {mean(durations):.4f}s, Avg Steps: {mean(steps):.2f}, Avg Neighbors: {mean(neighbors):.2f}")


# EXP 5: Si ara no servir a un client garantit tmb és solució vàlida, com se'ls hauria de penalitzar a la funció heurística? (HC i SA)
schedule = exp_schedule(k=10000, lam=0.00007, limit=100000)
def experiment_5():
    penalties = (0, 100, 500, 2000, 10000)
    for algorithm in ("HC", "SA"):
        for penalty in penalties:
            values, durations, steps, neighbors, unserved_guaranteed, profits = [], [], [], [], [], []
            for params in escenaris:
                config = replace(params, ini_sol_type=3, guaranteed_penalty=penalty)
                if algorithm == "HC":
                    e = EnergyNetworkProblem(config)
                else:
                    e = EnergyNetworkProblemSA(config)
                ip = InstrumentedProblem(e)

                random.seed(params.seed)
                start = time.perf_counter()
                if algorithm == "HC":
                    solution = hill_climbing(ip)
                else:
                    solution = simulated_annealing(ip, schedule)
                duration = time.perf_counter() - start

                unserved = 0
                for cust_i, plant_i in enumerate(solution.network):
                    customer = e.customers[cust_i]
                    if plant_i is None and customer.contract_type == 0:
                        unserved += 1

                profit, _ = profit_and_losses(e, solution)
                value = e.value(solution)
                profits.append(profit)
                unserved_guaranteed.append(unserved)
                values.append(value)
                durations.append(duration)
                steps.append(ip.succs-1)
                neighbors.append(ip.states) 

            print(f"Algorithm: {algorithm}, Penalty: {penalty}, Avg Unserved: {mean(unserved_guaranteed):.2f}, "
                  f"Max Unserved: {max(unserved_guaranteed)}, Avg Profit: {mean(profits):.2f} €, "
                  f"Avg Value: {mean(values):.2f}, Avg Duration: {mean(durations):.4f}s, Avg Steps: {mean(steps):.2f}")
                

# EXP 6: Si canvia la proporció de central de tipus C, s'usen menys les de tipus A i B? (HC i SA)
def experiment_6():
    configuracions = (
        (5, 10, 25),
        (5, 10, 50),
        (5, 10, 75),
    )

    for algorithm in ("HC", "SA"):
        for centrals_per_tipus in configuracions:
            values, profits, losses, durations, expansions, neighbors = [], [], [], [], [], []
            plants_a, plants_b, plants_c = [], [], []

            for params in escenaris:
                config = replace(params, count=1000, counts=list(centrals_per_tipus))

                if algorithm == "HC":
                    e = EnergyNetworkProblem(config)
                else:
                    e = EnergyNetworkProblemSA(config)

                if e.initial is None:
                    continue

                ip = InstrumentedProblem(e)
                random.seed(params.seed)

                start = time.perf_counter()
                if algorithm == "HC":
                    solution = hill_climbing(ip)
                else:
                    solution = simulated_annealing(ip, schedule)
                duration = time.perf_counter() - start

                value = e.value(solution)
                profit, lost_mw = profit_and_losses(e, solution)
                values.append(value)
                profits.append(profit)
                losses.append(lost_mw)
                durations.append(duration)
                expansions.append(ip.succs)
                neighbors.append(ip.states)

                used_plants = { plant_i for plant_i in solution.network if plant_i is not None}
                
                plants_a.append(sum(e.power_plants[p].plant_type == 0 for p in used_plants))
                plants_b.append(sum(e.power_plants[p].plant_type == 1 for p in used_plants))
                plants_c.append(sum(e.power_plants[p].plant_type == 2 for p in used_plants))

            print(f"Algorithm: {algorithm}, Centrals: {centrals_per_tipus}, valid: {len(values)}/{len(escenaris)}, "
                  f"Avg A on: {mean(plants_a):.2f}, Avg B on: {mean(plants_b):.2f}, Avg C on: {mean(plants_c):.2f}, "
                  f"Avg Value: {mean(values):.2f}, Avg Profit: {mean(profits):.2f} €, Avg Lost: {mean(losses):.2f} MW, "
                  f"Avg Duration: {mean(durations):.4f}s, Avg Expansions: {mean(expansions):.2f}, "
                  f"Avg Neighbors: {mean(neighbors):.2f}")


if __name__ == "__main__":
    experiment_2()
