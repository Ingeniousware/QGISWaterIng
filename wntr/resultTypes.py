class ResultNode():
    """Representa un tipo de Nodo para guadar los datos en un JSON
    
    Parameters
    ----------
    base_demand : float
        Valor de la demanda base del nodo.
    demand : float
        Demanda del nodo.
    pressure : float
        Presión del nodo.
    head : float
        Carga total en el nodo.
    """
    def __init__(self, base_demand = 0.0, demand = 0.0, pressure = 0.0, head = 0.0):
        self.BASE_DEMAND: float = base_demand
        self.DEMAND: float = demand
        self.PRESSURE: float = pressure
        self.HEAD: float = head
    
    def to_dict(self):
        return {
            "BASE DEMAND": self.BASE_DEMAND,
            "DEMAND": self.DEMAND,
            "PRESSURE": self.PRESSURE,
            "HEAD": self.HEAD}

class ResultLink():
    """Representa un tipo de link para guadar los datos en un JSON
    
    Parameters
    ----------
    lps : float
        Valor de caudal que sircula por la tuberia.
    headloss : float
        Pérdida de carga en la tuberia.
    status : any
        Estado de la tuberia. Abierta o Cerrada.
    diameter : float
        Diametro de la tuberia.
    minorloss : float
        Pérdidas menores en la tuberia.
    """
    def __init__(self, lps, headloss, status, diameter, minorloss):
        self.LPS: float = lps
        self.HEADLOSS: float = headloss
        self.STATUS = status
        self.DIAMETER: float = diameter
        self.MINORLOSS: float = minorloss
    
    def to_json(self):
        return{"LPS": self.LPS,
               "HEADLOSS": self.HEADLOSS,
               "STATUS": self.STATUS,
               "DIAMETER": self.DIAMETER,
               "MINORLOSS": self.MINORLOSS}