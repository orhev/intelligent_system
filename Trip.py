import numpy as np
class Trip:
    def __init__(self,trip_id,route_id, days,start_date,end_date):
        self.trip_id = trip_id
        self.route_id = route_id
        self.stops = np.array([])
        self.times = np.array([])
        self.days = days
        self.start_date = start_date
        self.end_date = end_date
