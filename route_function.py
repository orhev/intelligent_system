from geopy.geocoders import Nominatim
from pyroutelib3 import Router
from geopy.distance import geodesic
import requests
import time



def get_address_landmark(address):
    """gets the latitude and longitude coordinates from point's address

    Parameters
    ----------
    address : str
        point's address with the following structure:
        "street name, number, city name and country"

    Returns
    -------
    tuple contain two floats
        (latitude, longitude)
    """
    geolocator = Nominatim(user_agent="or")
    location = geolocator.geocode(address)
    return location.latitude, location.longitude


def get_route(start_point, end_point, transport_modes):
    """gets the route between start_point and end_point.

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
    Returns
    -------
    route : list
        A route between start point and end point as a list of coordinates nodes
    """
    if type(start_point) == str:
        start_gps = get_address_landmark(start_point)
    else:
        start_gps = start_point

    if type(end_point) == str:
        end_gps = get_address_landmark(end_point)
    else:
        end_gps = end_point
    # Router returns (status, node_ids_list) tuple as a result of routing between start_node_id and end_node_id.
    router = Router(transport_modes)

    # Find start and end nodes
    start_point = router.findNode(start_gps[0], start_gps[1])
    end_point = router.findNode(end_gps[0], end_gps[1])

    status, route = router.doRoute(start_point, end_point)
    if status == 'success':
        # convert node_ids to coordinates
        route_lat_lons = list(map(router.nodeLatLon, route))
        return route_lat_lons
    return []


def get_route_distance(route):
    """calculates the length of the route according to the distance between every 2 points.
    Parameters
    ----------
    route : list
        A route between start point and end point as a list of coordinates nodes

    Returns
    -------
    distance : int
        The the length of the route (km)
    """

    distance = 0
    if route:
        for i in range(len(route) - 1):
            distance += geodesic(route[i], route[i + 1]).km

    return distance


def get_elevation(route):
    """Returns the point height (height above sea level)

    Parameters
    ----------
    route : list
        A route between start point and end point as a list of coordinates nodes (latitude, longitude)

    Returns
    -------
    elevation : float
        The point height (height above sea level)
    """
    query = ""
    for i in range(len(route)):
        query += str(route[i][0]) + ',' + str(route[i][1]) + '|'
    query = 'https://api.opentopodata.org/v1/mapzen?locations=' + query
    query = query[0:len(query) - 1]
    r = requests.get(query).json()
    # extract elevation value from json object
    elevation = [r['results'][index]['elevation'] for index in range(len(r['results']))]
    return elevation


def get_route_incline(route):
    """Returns the average incline and maximum incline

    Parameters
    ----------
    route : list
        A route between start point and end point as a list of coordinates nodes

     Returns
    -------
    incline : tuple
        (average incline, max incline)
    """
    incline = []

    if route:
        elevation = get_elevation(route)
        for i in range(len(route) - 1):
            distance = geodesic(route[i], route[i + 1]).m
            incline.append(((elevation[i+1] - elevation[i]) / distance) * 100)

    return sum(incline) / len(incline), max(incline)


def route_score(route, weights):
    """
    Returns the route score according to its weights and property values

        Parameters
        ----------
        route : Route object
        weights : dictionary
            A dictionary that contains the route properties as its keys
            and the weight values of each property as its values.

         Returns
        -------
        score : float
           score route
        """
    score = 0
    for parameter in weights.keys():
        score += route.parameter * weights[parameter]
    return score



