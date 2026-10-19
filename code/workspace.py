from customers import generate_customers
from power_plants import generate_power_plants
import random as r





customers = generate_customers(5, [0.9, 0.05, 0.05], 0.5, r.random())
power_plants = generate_power_plants([1, 2, 3], r.random())

print(customers)
print()
print(power_plants)

