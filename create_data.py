from BusStop import BusStop
from Trip import Trip
from BusRoute import BusRoute
import pandas as pd
import dill
from dill import dump
from tqdm import tqdm
import numpy as np
from datetime import datetime, timedelta

# opening all necessary csv files
cluster_file = pd.read_csv(r'ClusterToLine.txt')
routes_csv = pd.read_csv("routes.txt")
stops_csv = pd.read_csv("stops.txt")
trips_csv = pd.read_csv("trips.txt")
stops_times = pd.read_csv("stop_times.txt")
calendar_csv = pd.read_csv("calendar.txt")
# getting all lines going through haifa city
only_haifa = cluster_file[cluster_file["OperatorLineId"].str.contains("חיפה")]
# getting lines_id for all lines in haifa
lines_in_haifa = only_haifa['OperatorName']
routes_desc = routes_csv['route_desc']
routes_in_haifa = routes_csv[routes_desc.str.contains('|'.join(lines_in_haifa.values.astype(str)))]
# all stops in haifa
stops_in_haifa = stops_csv[stops_csv['stop_desc'].str.contains('חיפה', na=False)]
stop_2_stop = {}

calendar_days = {}
# create dict with all stops as keys
for index, stops in stops_in_haifa.iterrows():
    stop_2_stop[stops['stop_id']] = BusStop(stops['stop_id'], stops['stop_code'], stops['stop_lat'],
                                            stops['stop_lon'], stops['stop_desc'])

# reorder all the trips going through haifa
routes_to_trips = {}
trips_in_haifa = trips_csv[trips_csv['route_id'].isin(routes_in_haifa['route_id'].values)]
trips_in_haifa = trips_in_haifa.sort_values(by=['trip_id'])
stops_times_in_haifa = stops_times[stops_times['trip_id'].isin(trips_in_haifa['trip_id'].values)]

i = 0
stops_in_route = []
day_changed = 0
stop_time = []
stop_times_count = stops_times_in_haifa['trip_id'].count()
# iterate over all trips
for index, trip in tqdm(trips_in_haifa.iterrows(), total=trips_in_haifa['trip_id'].count()):
    trip_id = trip['trip_id']
    service_times = calendar_csv[calendar_csv['service_id'] == trip['service_id']].squeeze()
    t = Trip(trip['trip_id'], trip['route_id'], service_times[
        ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']].values.squeeze(),
             datetime.strptime(str(service_times['start_date']), '%Y%m%d'),
             datetime.strptime(str(service_times['end_date']), '%Y%m%d'))
    # iterate all stops in a trip
    while i < stop_times_count and stops_times_in_haifa.iloc[i]['trip_id'] == trip_id:

        trip_stop = stops_times_in_haifa.iloc[i]
        stops_in_route.append(trip_stop['stop_id'])
        t.stops = np.append(t.stops, trip_stop['stop_id'])

        # fixing day changing in the middle of a trip
        if int(trip_stop['arrival_time'].split(":")[0]) >= 24:
            ts = datetime.strptime(str(int(trip_stop['arrival_time'].split(":")[0]) - 24)
                                   + trip_stop['arrival_time'][2:], "%H:%M:%S")
        else:
            ts = datetime.strptime(trip_stop['arrival_time'], "%H:%M:%S")
        if stop_time and stop_time > ts:
            day_changed = 1
        if day_changed:
            ts = ts + timedelta(days=1)

        t.times = np.append(t.times, ts)

        # connect all stops that have the same lines
        for past_stop in stops_in_route[0:-1]:
            if past_stop in stop_2_stop:
                if trip_stop['stop_id'] in stop_2_stop[past_stop].stops:
                    stop_2_stop[past_stop].stops[trip_stop['stop_id']].add(trip['route_id'])
                else:
                    stop_2_stop[past_stop].stops[trip_stop['stop_id']] = {trip['route_id']}

        i = i + 1
        stop_time = ts
    stops_in_route = []
    stop_time = []
    day_changed = 0

    # connect a trip to his route
    if not trip['route_id'] in routes_to_trips:
        ro = routes_in_haifa[routes_in_haifa['route_id'] == trip['route_id']].squeeze()
        routes_to_trips[trip['route_id']] = BusRoute(ro['route_short_name'], ro['route_long_name'], ro['route_desc'])
    routes_to_trips[trip['route_id']].trips[trip['trip_id']] = t

# save models

with open('trips_to_stops.pickle', 'wb') as handle:
    dump(routes_to_trips, handle, dill.HIGHEST_PROTOCOL)

with open('stops_with_routes.pickle', 'wb') as handle:
    dump(stop_2_stop, handle, dill.HIGHEST_PROTOCOL)
