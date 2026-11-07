import random
import time

from aima.search import hill_climbing, InstrumentedProblem
from problem import EnergyNetworkProblem, Params
from network_state import EnergyNetworkState
from operators import Move, Swap


def describe(problem, state):
    #retorna les mètriques "reals" d'un estat (no només el valor de la heurística)
    plants_on = [problem.power_plants[p].production_mw - e > 1e-6 for p, e in enumerate(state.plants_available_energy)]
    on_by_type = [sum(1 for p, on in enumerate(plants_on) if on and problem.power_plants[p].plant_type == t) for t in range(3)]
    total_by_type = [sum(1 for plant in problem.power_plants if plant.plant_type == t) for t in range(3)]

    served = [plant_i is not None for plant_i in state.network]
    lost_mw = sum(problem.loss_matrix[c][p] for c, p in enumerate(state.network) if p is not None)
    used_mw = sum(plant.production_mw - e for plant, e in zip(problem.power_plants, state.plants_available_energy))
    capacity_mw = sum(plant.production_mw for plant in problem.power_plants)

    #la heurística és h = benefici - w1 * MW perduts  ->  benefici = h + w1 * MW perduts
    h = problem.value(state)
    profit = h + problem.w1 * lost_mw

    return {
        "heurística": h,
        "benefici (€)": profit,
        "MW perduts": lost_mw,
        "MW usats / capacitat": f"{used_mw:.0f} / {capacity_mw:.0f} ({100*used_mw/capacity_mw:.1f} %)",
        "centrals enceses (A, B, C)": f"{sum(plants_on)}/{len(plants_on)}  ({on_by_type[0]}/{total_by_type[0]}, {on_by_type[1]}/{total_by_type[1]}, {on_by_type[2]}/{total_by_type[2]})",
        "clients servits": f"{sum(served)}/{len(served)}",
        "garantits sense servir": sum(1 for c, s in zip(problem.customers, served) if not s and c.contract_type == 0),
        "no garantits sense servir": sum(1 for c, s in zip(problem.customers, served) if not s and c.contract_type == 1),
    }


def main():

    ##----------------------EXAMPLE USE---------------------##

    #escenari de l'experiment 1 (amb 1000 clients el Hill Climbing tarda ~1 minut; baixeu count per provar ràpid)
    config_exemple = Params(
        seed=12,
        counts=[5, 10, 25],
        count=100,
        type_proportions=[0.25, 0.30, 0.45],
        guaranteed_proportion=0.75,
        weights = [0.01]
    )
    operators = (Move, Swap)
    sol_type = 2

    problem_exemple = EnergyNetworkProblem(config_exemple, operators, sol_type)
    if problem_exemple.initial is None:
        print("La solució inicial no és vàlida per aquesta instància")
        return

    #InstrumentedProblem compta les crides a actions() (passos) i a result() (veïns generats)
    instrumented = InstrumentedProblem(problem_exemple)

    random.seed(config_exemple.seed) #hill_climbing desempata a l'atzar: així és reproduïble
    start = time.perf_counter()
    solution = hill_climbing(instrumented)
    duration = time.perf_counter() - start

    #recalculem el valor final des de zero (sense l'acumulació de l'increment)
    solution = EnergyNetworkState(solution.network, solution.plants_available_energy)

    initial_info = describe(problem_exemple, problem_exemple.initial)
    final_info = describe(problem_exemple, solution)

    print(f"Seed {config_exemple.seed}, {config_exemple.count} clients, centrals {list(config_exemple.counts)}, "
          f"operadors {[op.__name__ for op in operators]}, sol_type {sol_type}, w1 {problem_exemple.w1}\n")
    print(f"{'':30}{'inicial':>30}{'final':>30}")
    for key in initial_info:
        ini, fin = initial_info[key], final_info[key]
        if isinstance(ini, float):
            print(f"{key:30}{ini:>30.2f}{fin:>30.2f}")
        else:
            print(f"{key:30}{str(ini):>30}{str(fin):>30}")

    print(f"\npassos: {instrumented.succs - 1}, veïns generats: {instrumented.states}, temps: {duration:.2f} s")

    ##------------------------------------------------------##

if __name__ == "__main__":
    main()
