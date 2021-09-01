from dill import load, dump
import dill
from datetime import timedelta
import time
import numpy as np
import datetime

start = time.time()
with open('trips_to_stops.pickle', 'rb') as handle:
    routes_to_trips = load(handle)
with open('stops_with_routes.pickle', 'rb') as handle:
    stop_2_stop = load(handle)

# stop_2_stop_id = {}
# for key, value in stop_2_stop.items():
#     stop_2_stop_id[value.stop_code] = key
#
# with open('stop_2_stop_id.pickle', 'wb') as handle:
#     dump(stop_2_stop_id, handle, dill.HIGHEST_PROTOCOL)

with open('stop_2_stop_id.pickle', 'rb') as handle:
    stop_2_stop_id = load(handle)

end = time.time()


# print(end - start)


def stop_to_stop_way(stop_id_start, stop_id_end, time_search, date_search, time_delta, max_jumps=0,
                     time_between_switches=timedelta(minutes=3)):
    trips_between_stops = {}
    if stop_id_start in stop_2_stop and stop_id_end in stop_2_stop[stop_id_start].stops:
        for lines in stop_2_stop[stop_id_start].stops[stop_id_end]:
            for key_trip, val_trip in routes_to_trips[lines].trips.items():
                if val_trip.start_date <= date_search <= val_trip.end_date and \
                        val_trip.days[date_search.weekday() - 1] == 1:
                    time_stop_start = np.argwhere(val_trip.stops == stop_id_start).squeeze().tolist()
                    if not type(time_stop_start) is list: time_stop_start = [time_stop_start]
                    for stop_start_idx in time_stop_start:
                        if datetime.timedelta(0) < val_trip.times[stop_start_idx] - time_search < time_delta:
                            # if val_trip.times[stop_start_idx] - time_search < time_delta:
                            time_stop_end_idx = np.argwhere(val_trip.stops == stop_id_end)
                            if len(np.where(time_stop_end_idx > stop_start_idx)[0]):
                                time_stop_end = np.min(time_stop_end_idx[np.where(time_stop_end_idx > stop_start_idx)])
                                stops_del = val_trip.times[time_stop_end] - val_trip.times[stop_start_idx]
                                # if (stop_id_start, stop_id_end) not in trips_between_stops:
                                #     trips_between_stops[(stop_id_start, stop_id_end)] = {}
                                if lines not in trips_between_stops or trips_between_stops[lines][1] > val_trip.times[stop_start_idx]:
                                        trips_between_stops[lines] = (key_trip, val_trip.times[stop_start_idx], stops_del,np.asscalar((time_stop_end_idx-stop_start_idx)[0]))

                                    # elif :
                                    #     trips_between_stops[lines] = (key_trip, val_trip.times[stop_start_idx], stops_del)

    if max_jumps == 0:
        return trips_between_stops
    else:

        chosen_trip = []
        # same bus stop switch
        for other_stops_key, other_stops_val in stop_2_stop[stop_id_start].stops.items():
            if other_stops_key in stop_2_stop and stop_id_end in stop_2_stop[other_stops_key].stops:
                start_to_middle = stop_to_stop_way(stop_id_start, other_stops_key, time_search, date_search, time_delta,
                                                   max_jumps - 1,
                                                   time_between_switches)
                for key_route, val_route in start_to_middle.items():
                    middle_to_end = stop_to_stop_way(other_stops_key, stop_id_end,
                                                     val_route[1] + val_route[2] + time_between_switches, date_search,
                                                     time_delta,
                                                     max_jumps - 1,
                                                     time_between_switches)

                    # chosen_trip = ((key_route,start_to_middle[(stop_id_start, other_stops_key)]),next(iter(middle_to_end[(other_stops_key,stop_id_end)])))
                    for switch_route_key, switch_route_val in middle_to_end.items():
                        if not key_route == switch_route_key:
                            if chosen_trip and delta > switch_route_val[1] + switch_route_val[2] - time_search or not chosen_trip:
                                chosen_trip = (other_stops_key, key_route, val_route, switch_route_key, switch_route_val)
                                delta = switch_route_val[1] + switch_route_val[2] - time_search
                        # else:
                        #     chosen_trip = (val_route,switch_route_val)
                        #     delta = switch_route_val[1] + switch_route_val[2] - time_search

    return [trips_between_stops, chosen_trip]

# start = time.time()
# [a,b] = stop_to_stop_way(stop_2_stop_id[41208], stop_2_stop_id[43000], datetime.datetime.strptime("14:00", "%H:%M"),
#                  datetime.datetime.strptime("20210821", '%Y%m%d'), timedelta(minutes=30), 1, timedelta(minutes=3))
# end = time.time()
# print((end - start))
