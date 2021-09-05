

class BusStop:
    def __init__(self, stop_id, stop_code, lat, lon, desc):
        self.stop_id = stop_id
        self.stop_code = stop_code
        self.lat = lat
        self.lon = lon
        self.desc = desc
        self.stops = {}
