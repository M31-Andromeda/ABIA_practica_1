from aima.search import hill_climbing, simulated_annealing, InstrumentedProblem, exp_schedule
from operators import Move, Swap
import time
from statistics import mean
import random 
from dataclasses import replace

from problem import EnergyNetworkProblem
from problem_sa import EnergyNetworkProblemSA
from parameters import Params
from resultats import guardar

import math

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

schedule = exp_schedule(k=0.01, lam=math.log(0.01/0.00001)/500_000, limit=500_000)


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
            guardar("exp1", {"operadors": "+".join(op.__name__ for op in operators), "seed": params.seed, "value": value, "profit": profit, "lost_mw": lost_mw, "temps": duration, "passos": ip.succs - 1, "veins": ip.states})

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
            guardar("exp2", {"ini_sol_type": ini_sol_type, "seed": params.seed, "value": value, "profit": profit, "lost_mw": lost_mw, "temps": duration, "passos": ip.succs - 1, "veins": ip.states})

        if not values:
            print(f"Initial Solution: {ini_sol_type}, cap solució inicial vàlida")
            continue

        print(f"Initial Solution: {ini_sol_type}, valid: {len(values)}/{len(escenaris)}, Avg Value: {mean(values):.2f}, "
              f"Avg Profit: {mean(profits):.2f} €, Avg Lost: {mean(losses):.2f} MW, Avg Duration: {mean(durations):.4f}s, "
              f"Avg Steps: {mean(steps):.2f}, Avg Neighbors: {mean(neighbors):.2f}")
            

# EXP 3: Quins paràmetres de Simulated Annealing són millors? 
def experiment_3A():

    for k in (0.01, 0.1, 1, 10, 100, 1000):
        for T_final in (0.1, 0.001, 0.00001):
            if T_final >= k:
                continue

            values, profits, losses, durations, iterations, neighbors = [], [], [], [], [], []
            max_iter = 500_000 # limit fixat arbitrareament per escollir la millor combinació de k y T_final, l'ajustarem mes endevant 
            lam = math.log(k/T_final)/max_iter

            for params in escenaris:
                e = EnergyNetworkProblemSA(params)
                random.seed(params.seed)
                ip = InstrumentedProblem(e)
                schedule = exp_schedule(k=k, lam=lam, limit=max_iter)

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
                guardar("exp3A", {"k": k, "T_final": T_final, "lam": lam, "limit": max_iter, "ini_sol_type": params.ini_sol_type, "seed": params.seed, "value": value, "profit": profit, "lost_mw": lost_mw, "temps": duration, "iteracions": ip.succs, "veins": ip.states})

            print(f"Initial solution: {params.ini_sol_type}, Temperature: {k}, T_final: {T_final}, Cooling: {lam}, "
                f"Limit: {max_iter}, Mean h: {mean(values):.2f}, Avg Profit: {mean(profits):.2f} €, "
                f"Avg Lost: {mean(losses):.2f} MW, Mean Duration: {mean(durations):.4f}s, "
                f"Avg Steps: {mean(iterations):.2f}, Avg Neighbors: {mean(neighbors):.2f}")

def experiment_3B():
    T_final = 0.00001
    k = 0.01
    for max_iter in (100_000, 250_000, 500_000, 1_000_000):
        lam = math.log(k/T_final)/max_iter

        values, profits, losses, durations, iterations, neighbors = [], [], [], [], [], []
        for params in escenaris:
            e = EnergyNetworkProblemSA(params)
            random.seed(params.seed)
            ip = InstrumentedProblem(e)
            schedule = exp_schedule(k=k, lam=lam, limit=max_iter)

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
            guardar("exp3B", {"k": k, "T_final": T_final, "lam": lam, "limit": max_iter, "ini_sol_type": params.ini_sol_type, "seed": params.seed, "value": value, "profit": profit, "lost_mw": lost_mw, "temps": duration, "iteracions": ip.succs, "veins": ip.states})

        print(f"Initial solution: {params.ini_sol_type}, Temperature: {k}, T_final: {T_final}, Cooling: {lam}, "
            f"Limit: {max_iter}, Mean h: {mean(values):.2f}, Avg Profit: {mean(profits):.2f} €, "
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
            guardar("exp4", {"clients": nombre_clients, "centrals": sum(centrals_per_tipus), "seed": params.seed, "value": value, "profit": profit, "lost_mw": lost_mw, "temps": duration, "passos": ip.succs - 1, "veins": ip.states})

        if not values:
            print(f"Clients: {nombre_clients}, Centrals: {sum(centrals_per_tipus)}{centrals_per_tipus}, cap solució inicial vàlida")
            continue

        print(f"Clients: {nombre_clients}, Centrals: {sum(centrals_per_tipus)}{centrals_per_tipus}, Valid: {len(values)}/{len(escenaris)}, "
              f"Avg Value: {mean(values):.2f}, Avg Profit: {mean(profits):.2f} €, Avg Lost: {mean(losses):.2f} MW, "
              f"Avg Duration: {mean(durations):.4f}s, Avg Steps: {mean(steps):.2f}, Avg Neighbors: {mean(neighbors):.2f}")


# EXP 5: Si ara no servir a un client garantit tmb és solució vàlida, com se'ls hauria de penalitzar a la funció heurística? (HC i SA)
def experiment_5():
    penalties = (0, 100, 500, 2000, 4000, 6000, 8000, 10000)
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
                guardar("exp5", {"algorisme": algorithm, "penalitzacio": penalty, "seed": params.seed, "garantits_sense_servir": unserved, "value": value, "profit": profit, "temps": duration, "passos": ip.succs - 1, "veins": ip.states})

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
                guardar("exp6", {"algorisme": algorithm, "centrals_ABC": "-".join(map(str, centrals_per_tipus)), "seed": params.seed, "A_on": plants_a[-1], "B_on": plants_b[-1], "C_on": plants_c[-1], "value": value, "profit": profit, "lost_mw": lost_mw, "temps": duration, "expansions": ip.succs, "veins": ip.states})

            print(f"Algorithm: {algorithm}, Centrals: {centrals_per_tipus}, valid: {len(values)}/{len(escenaris)}, "
                  f"Avg A on: {mean(plants_a):.2f}, Avg B on: {mean(plants_b):.2f}, Avg C on: {mean(plants_c):.2f}, "
                  f"Avg Value: {mean(values):.2f}, Avg Profit: {mean(profits):.2f} €, Avg Lost: {mean(losses):.2f} MW, "
                  f"Avg Duration: {mean(durations):.4f}s, Avg Expansions: {mean(expansions):.2f}, "
                  f"Avg Neighbors: {mean(neighbors):.2f}")



# Teniu `w1 = 0.01`, que penalitza els MW perduts, però no el varieu enlloc. Afegiu un experiment
#  petit amb HC i `w1` a 0, 0.01, 1, 10 i 100, i compareu benefici, MW perduts i temps.
def experiment_A():
    weights = (0, 0.01, 1, 10, 100)
    for w in weights:
        values, durations, steps, neighbors, profits, losses,  = [], [], [], [], [], []
        for params in escenaris:
            config = replace(params, weights = [w])
            e = EnergyNetworkProblem(config)
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
            steps.append(ip.succs-1)
            neighbors.append(ip.states)

            guardar("expA", {"w1": w, "seed": params.seed, "value": value, "profit": profit, "lost_mw": lost_mw,
                             "temps": duration, "passos": ip.succs - 1, "veins": ip.states})

        print(f"Weight: {w}, Avg Value: {mean(values):.2f}, Avg Profit: {mean(profits):.2f} €, "
              f"Avg Lost: {mean(losses):.2f} MW, Avg Duration: {mean(durations):.4f}s, "
              f"Avg Steps: {mean(steps):.2f}, Avg Neighbors: {mean(neighbors):.2f}")

# Comparar resultats de HC i SA amb les mateixes condicions (operadors, sol inicial).
# Millor model de HC vs millor model de SA.
def experiment_B():
    
    for algorithm in ("HC", "SA"):
        values, durations, steps, neighbors, profits, losses = [], [], [], [], [], []
        for params in escenaris:
            config = replace(params)

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
                solution = simulated_annealing(ip, schedule) #schedule escollit a l'experiment 3
            duration = time.perf_counter() - start
            value = e.value(solution)
            profit, lost_mw = profit_and_losses(e, solution)
            nsteps = ip.succs - 1 if algorithm =="HC" else ip.succs

            values.append(value)
            profits.append(profit)
            losses.append(lost_mw)
            durations.append(duration)
            steps.append(nsteps)
            neighbors.append(ip.states)

            guardar("expB", {"algorisme": algorithm, "seed": params.seed, "value": value, "profit": profit,
                             "lost_mw": lost_mw, "temps": duration, "passos_o_iteracions": nsteps, "veins": ip.states})

        print(f"Algorithm: {algorithm}, valid: {len(values)}/{len(escenaris)}, Avg Value: {mean(values):.2f}, "
              f"Avg Profit: {mean(profits):.2f} €, Avg Lost: {mean(losses):.2f} MW, Avg Duration: {mean(durations):.4f}s, "
              f"Avg Steps/Iter: {mean(steps):.2f}, Avg Neighbors: {mean(neighbors):.2f}")

if __name__ == "__main__":
    #ús: python experiments.py 1 2 3A ... (els experiments que es vulguin executar)
    import sys
    experiments = {"1": experiment_1, "2": experiment_2, "3A": experiment_3A, "3B": experiment_3B, "4": experiment_4,
                   "5": experiment_5, "6": experiment_6, "A": experiment_A, "B": experiment_B}
    for nom in sys.argv[1:]:
        experiments[nom]()
