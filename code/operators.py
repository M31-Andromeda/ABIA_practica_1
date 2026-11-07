class Move:
    "Canvia la central d'un client: assignar (None -> central), desassignar (central -> None) o moure (central -> central)."
    def __init__(self, cust_i, orig, desti):
        self.cust_i = cust_i
        self.orig = orig
        self.desti = desti        

    def __repr__(self):
        return f"Move({self.cust_i}, {self.orig}, {self.desti})"

class Swap:
    "Intercanvia dos clients servits per dues centrals diferents"
    def __init__(self, cust_i, cust_j):
        self.cust_i = cust_i
        self.cust_j = cust_j
        
    def __repr__(self):
        return f"Swap({self.cust_i}, {self.cust_j})"
        

