from problem import EnergyNetworkProblem, Params
from network_state import EnergyNetworkState


def main():

    ##----------------------EXAMPLE USE---------------------##

    config_exemple = Params(
        seed=12,
        counts=[5, 10, 25],
        count=5,
        type_proportions=[0.25, 0.30, 0.45],
        guaranteed_proportion=0.75
    )

    problem_exemple = EnergyNetworkProblem(config_exemple)

    print(problem_exemple.supply_matrix[4])


    ##------------------------------------------------------##

if __name__ == "__main__":
    main()   