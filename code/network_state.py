
class EnergyNetworkState:
    """
    State class on l'estat del problema es guarda en una tupla on
    l'index indica el client o usuari de la xarxa i l'element de la tupla
    indica a quina central està connectada (None si no està servit).
    A més, plants_available_energy guarda per a cada central els MW que encara té lliures.

    Per exemple, amb 3 clients i 3 centrals:
    network = (2, None, 0)  -> el client 0 va a la central 2, el client 1 no està servit
                               i el client 2 va a la central 0
    plants_available_energy = (480.0, 120.0, 37.5)  -> MW lliures de les centrals 0, 1 i 2

    """
    def __init__(self, assignation, plants_available_energy):
        self.network = tuple(assignation)
        self.plants_available_energy = tuple(plants_available_energy)
        self.value = None

    def __hash__(self):
        return hash(self.network)

    def __eq__(self, other):
        return isinstance(other, EnergyNetworkState) and self.network == other.network








