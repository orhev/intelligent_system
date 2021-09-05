class BusRoute:
    def __init__(self, sn, ln, desc):
        self.sn = sn
        self.ln = ln
        self.desc = desc
        self.trips = {}
