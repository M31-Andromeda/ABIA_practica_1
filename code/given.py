#Accés al codi donat (given_code/) des de code/: és l'únic lloc on es toca el sys.path.
#La resta de fitxers importen d'aquí el que necessiten del codi donat.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "given_code"))

from customers import generate_customers
from power_plants import generate_power_plants
from energy import (
    get_guaranteed_tariff,
    get_non_guaranteed_tariff,
    get_non_service_penalty,
    get_production_cost_per_mw,
    get_running_cost,
    get_stopped_cost,
    get_loss_fraction,
)
