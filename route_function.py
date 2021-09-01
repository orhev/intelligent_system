from geopy.geocoders import Nominatim
from pyroutelib3 import Router
import requests
import folium
import haversine as hs
from haversine import Unit



def get_address_landmark(address):
    """
    Gets the latitude and longitude coordinates from point's address

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
    """
    Gets the route between start_point and end_point.

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
    """
    Calculates the length of the route according to the distance between every 2 points.
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
            distance += hs.haversine(route[i], route[i + 1])

    return distance


def get_elevation(route):
    """
    Returns the point height (height above sea level)

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


def incline_along_route(route):
    """
    Calculate the inclines and distances between two consecutive points in the route

    Parameters
    ----------
    route : list
        A route between start point and end point as a list of coordinates nodes (latitude, longitude)

    Returns
    -------
    incline, distance : tuple (list, list)
        A tuple contains a list of the inclines and distances between two consecutive points in the route

    """

    incline = []
    distance = []

    if route:
        elevation = get_elevation(route)
        for i in range(len(route) - 1):
            distance.append(hs.haversine(route[i], route[i + 1], unit=Unit.METERS))
            incline.append(((elevation[i + 1] - elevation[i]) / distance[i]) * 100)

    return incline, distance

def get_route_incline(routes):
    """
    Returns the average incline and maximum incline

    Parameters
    ----------
    routes : two list
        A route between start point and bus station as a list of coordinates nodes
        and a route between bus station  and end point as a list of coordinates nodes

     Returns
    -------
    incline : tuple
        (average incline, max incline)
    """
    incline = []
    ava_incline = 0
    max_incline = 0
    for r in routes:
        if r:
            inc, dis = incline_along_route(r)
            incline = incline + inc

    ava_incline = sum(incline) / len(incline)
    max_incline = max(incline)
    return ava_incline, max_incline


def sharp_incline(routes):
    """
    Calculate the length of the route (in meters) with a sharp slope (above 10%)
    and the percentage of this sub-route (with  a sharp slope) of the total route

    Parameters
    ----------
    routes : tow list
        A route between start point and bus station as a list of coordinates nodes
        and a route between bus station  and end point as a list of coordinates nodes

    Returns
    -------
    length, percentage : tuple (flat, flat)
        The length of the route with a sharp slope
        the percentage of this sub-route with  a sharp slope
    """
    incline = []
    distance = []

    for r in routes:
        inc, dis = incline_along_route(r)
        incline = incline + inc
        distance = distance + dis

    tot_route = routes[0] + routes[1]
    if tot_route:
        distance_sharp_incline = [distance[i] for i in range(len(distance)) if incline[i] > 10]
        return int((sum(distance_sharp_incline) / sum(distance_sharp_incline)) * 100), int(sum(distance_sharp_incline))

    return 0, 0


def route_incline_parameters(route_forth, route_back):

    """
    Returns the route incline parameters will give in the following order:
        ['average incline', 'maximum incline', 'sharp incline percent', 'sharp incline distance']

        Parameters
        ----------
        route_forth : List
        A route between start point and bus station as a list of coordinates nodes
        route_back : List
        A route between bus station  and end point as a list of coordinates nodes


         Returns
        -------
        parameters : List

        """

    avg_incline,  max_incline = get_route_incline([route_forth, route_back])
    sharp_incline_percent, sharp_incline_distance = sharp_incline([route_forth, route_back])
    parameters = [avg_incline, max_incline, sharp_incline_percent, sharp_incline_distance]
    return parameters


def get_route_map(route, zoom=15):
    """
        Creates a map with the starting point, the end point and the route

        Parameters
        ----------
        route : list
            A route between start point and end point as a list of coordinates nodes
        zoom : int
            De
    """

    start_coordinates = [route[0][0], route[0][1]]
    end_coordinates = [route[-1][0], route[-1][1]]
    tooltip = 'Click For More Info'
    m = folium.Map(location=start_coordinates, zoom_start=zoom)
    folium.Marker(start_coordinates, popup='<strong>Start Location</strong>', tooltip=tooltip).add_to(m)
    folium.Marker(end_coordinates, popup='<strong>End Location</strong>', tooltip=tooltip).add_to(m)
    folium.PolyLine(route, color='red', weight=10, opacity=0.8).add_to(m)
    m.save('map.html')


