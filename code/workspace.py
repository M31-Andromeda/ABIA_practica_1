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

def percentatge_mill(val_0, val_1):
    return round((val_1-val_0)/val_0 *100, 2)



escenari = escenaris[3]

e = EnergyNetworkProblem(escenari)
ip = InstrumentedProblem(e)
random.seed(escenari.seed)

print("Initializing problem")
start = time.perf_counter()
solution_hc = hill_climbing(ip)
solution_sa = simulated_annealing(ip)
duration = time.perf_counter() - start
print(f"Problems finished duration: {round(duration, 2)}")


profit_ini, lost_mw_ini = profit_and_losses(e, e.initial)
profit_final_hc, lost_mw_final_hc = profit_and_losses(e, solution_hc)
profit_final_sa, lost_mw_final_sa = profit_and_losses(e, solution_sa)



print(f"profit ini: {profit_ini}, profit final hc: {profit_final_hc}, millora hc:{percentatge_mill(profit_ini, profit_final_hc)}%")
print(f"lost MW ini: {lost_mw_ini}, lost MW final hc: {lost_mw_final_hc}, millora hc: {percentatge_mill(lost_mw_ini, lost_mw_final_hc)}%")

print(f"profit ini: {profit_ini}, profit final sa: {profit_final_sa}, millora sa:{percentatge_mill(profit_ini, profit_final_sa)}%")
print(f"lost MW ini: {lost_mw_ini}, lost MW final sa: {lost_mw_final_sa}, millora sa: {percentatge_mill(lost_mw_ini, lost_mw_final_sa)}%")
