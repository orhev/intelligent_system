import route_function as rf


class Route:
    """
    A class used to represent a chosen route from point "start" to "end"

    ...

    Attributes
    ----------
    start_point : str or tuples
        starting point address or coordinates
    end_point : str or tuples
        ending point address or coordinates
    transport_modes : str
       transportation profiles
    start_gps : tuples
        latitude and longitude coordinates with the following structure:
            (latitude, longitude) -  tuples contain two floats
    end_gps : tuples
        latitude and longitude coordinates with the following structure:
            (latitude, longitude) -  tuples contain two floats
    route : list
        A route between start point and end point as a list of coordinates nodes
    length : float
        the length of the route
    avg_incline : float
        The average incline along the route
    max_incline : float
        The maximum incline along the route


    Methods
    -------
    return_properties

    """

    def __init__(self, start_point, end_point, transport_modes):
        """
        Parameters
        ----------
        start_point : str or tuples
            starting point address or coordinates
            The starting point can be given as a string (address) with the following structure:
            "street name, number, city name and country"
            or as latitude and longitude coordinates with the following structure:
            (latitude, longitude)-  tuples contain two floats
        end_point : str or tuples
            ending point address or coordinates
            Same as start_point
        transport_modes : str
            transportation profiles choose from a default list of profiles:
            car, bus, cycle, horse, foot, tram, train
        """
        self.start_point = start_point
        self.end_point = end_point
        self.transport_modes = transport_modes

        if type(self.start_point) == str:
            self.start_gps = rf.get_address_landmark(self.start_point)
        else:
            self.start_gps = self.start_point

        if type(self.end_point) == str:
            self.end_gps = rf.get_address_landmark(self.end_point)
        else:
            self.end_gps = self.end_point

        self.route = rf.get_route(self.start_gps, self.end_gps, self.transport_modes)
        self.length = rf.get_route_distance(self.route)
        incline = rf.get_route_incline(self.route)
        self.avg_incline = incline[0]
        self.max_incline = incline[1]

    def return_properties(self):
        properties = {'length': self.length, 'avg_incline': self.avg_incline,
                             'max_incline': self.max_incline, 'num_of_bus_exchange': int,
                             'travle_time': float}
        return properties





