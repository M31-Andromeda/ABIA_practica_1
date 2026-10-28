 

class EnergyNetworkState:
    """
    State class on l'estat del problema es guarda en una tupla on
    l'index indica el client o usuari de la xarxa i l'element de la tupla
    indica a quina centralestà conectada. 

    Per exemple:
    tuple() ##FALTA EXEMPLE
    
    """
    def __init__(self, assignation, plants_available_energy):
        
        self.network = tuple(assignation)
        self.plants_available_energy = plants_available_energy

    def get_actions(self):
        pass

    def apply_action(self, action):
        pass

    def __hash__(self):
        return hash(self.network)

    def __eq__(self, other):
        return isinstance(other, EnergyNetworkState) and self.network == other.network

    def __repr__(self):
        #TODO
        return super().__repr__()








