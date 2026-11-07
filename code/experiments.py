from aima.search import hill_climbing, simulated_annealing, InstrumentedProblem, exp_schedule
from problem import EnergyNetworkProblem, Params
from operators import Move, Swap
import time
from statistics import mean


escenaris = [Params(seed=seed, counts=[5, 10, 25], count=1000,
                    type_proportions=[0.25, 0.30, 0.45], guaranteed_proportion=0.75, weights=[0.01])
                    for seed in range(20)]


# EXP 1: Move sol o Move + Swap, quin va millor? (Hill Climbing)
def experiment_1():
    for operators in ((Move,), (Move, Swap)):
        values = []
        durations = []
        steps = []
        neighbors = []

        for params in escenaris:
            e = EnergyNetworkProblem(params, operators)
            ip = InstrumentedProblem(e)
            start = time.perf_counter()
            solution = hill_climbing(ip)
            duration = time.perf_counter() - start

            value = e.value(solution)
            values.append(value)
            durations.append(duration)
            steps.append(ip.succs - 1)
            neighbors.append(ip.states)
            #print(f"Operators: {operators}, Seed: {params.seed}, Value: {value}, Duration: {duration:.4f}s")
        
        print(f"Operators: {operators}, Avg Value: {mean(values):.2f}, Avg Duration: {mean(durations):.4f}s, "
              f"Avg Steps: {mean(steps):.2f}, Avg Neighbors: {mean(neighbors):.2f}")
            
            

# EXP 2: Quina solució inicial és millor? (Hill Climbing)
def experiment_2():
    for sol_type in (0,1,2):
        values = []
        durations = []
        steps = []
        neighbors = []

        for params in escenaris:
            e = EnergyNetworkProblem(params, (Move, Swap), sol_type)

            if e.initial is None:
                raise ValueError(f"Initial solution not valid: type {sol_type}, seed {params.seed}")    # per si no tenim una sol. inicial vàlida 

            ip = InstrumentedProblem(e)

            start = time.perf_counter()
            solution = hill_climbing(ip)
            duration = time.perf_counter() - start

            value = e.value(solution)
            values.append(value)
            durations.append(duration)
            steps.append(ip.succs - 1)          # d'actions (i restem 1 per l'estat final que no el volem comptar)
            neighbors.append(ip.states)         # de result

        print(f"Operators: {operators}, Avg Value: {mean(values):.2f}, Avg Duration: {mean(durations):.4f}s, "
              f"Avg Steps: {mean(steps):.2f}, Avg Neighbors: {mean(neighbors):.2f}")
            

# EXP 3: Quins paràmetres de Simulated Annealing són millors? 
def experiment_3():
    configuracions = (        # valors extrems 
        (1, 0.01, 3000),      # Temperatura molt baixa, refredament ràpid
        (1000, 0.1, 3000),    # Temperatura alta, refredament ràpid
        (1, 0.0001, 3000),    # Temperatura baixa, refredament lent
        (1000, 0.0001, 3000), # Temperatura alta, refredament lent
    )

    for temperatura_incial, refredament, max_iterations in configuracions:
        values =[]
        durations = []
        iterations = []
        neighbors = []

        for params in escenaris:
            e = EnergyNetworkProblem(params, (Move, Swap), sol_type)

            ip = InstrumentedProblem(e)

            schedule = exp_schedule(k=temperatura_incial, lam=refredament, limit=max_iterations)

            start = time.perf_counter()
            solution = simulated_annealing(ip, schedule)
            duration = time.perf_counter() - start

            value = e.value(solution)
            values.append(value)
            durations.append(duration)
            iterations.append(ip.succs) # aquí mesurem les expansions no els moviments acceptats
            neighbors.append(ip.states)

        print(f"Initial solution: {sol_type}, Temperature: {temperature_inicial}, Cooling: {refredament}, "
              f"Limit: {max_iterations}, Avg Value: {mean(values):.2f}, Avg Duration: {mean(durations):.4f}s, "
              f"Avg Steps: {mean(steps):.2f}, Avg Neighbors: {mean(neighbors):.2f}")



# EXP 4: Com creix el temps d'execució amb el nombre de clients o centrals? (Hill Climbing)
def experiment_4():
    pass    

# EXP 5: Si ara no servir a un client garantit tmb és solució vàlida, com se'ls hauria de penalitzar a la funció heurística? (HC i SA)
def experiment_5():
    pass

# EXP 6: Si canvia la proporció de central de tipus C, s'usen menys les de tipus A i B? (HC i SA)
def experiment_6():
    pass


if __name__ == "__main__":
    experiment_1()
    experiment_2()
    experiment_3()
    experiment_4()
    experiment_5()
    experiment_6()