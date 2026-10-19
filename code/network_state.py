
class EnergyNetworkState:
    """
    State class on l'estat del problema es guarda en una tupla on
    l'index indica el client o usuari de la xarxa i l'element de la tupla
    indica a quina centralestà conectada. 

    Per exemple:
    tuple() ##FALTA EXEMPLE
    
    """
    def __init__(self, network : tuple):
        self.network = tuple(network)



