from tkcalendar import Calendar, DateEntry
from datetime import datetime, timedelta
from create_way import stop_2_stop, stop_to_stop_way, routes_to_trips
from route_function import *
import itertools
from Recommender_System import *
from bus_row_gui import RowRouteContainer
from feedback_page import *
import numpy as np
from tkinter import messagebox
import csv

# flip bottom: switch between the two addresses
def flip_address(entry_to, entry_from):
    a = entry_from.get()
    entry_from.delete(0, 'end')
    entry_from.insert(0, entry_to.get())
    entry_to.delete(0, 'end')
    entry_to.insert(0, a)


# a function called by a bottom
# writes the user review in a csv file with other parameters that define the route chosen
def open_feedback(all_routes_params):
    score, id = get_score_from_feedback()
    with open(r'user_preferred_data', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([all_routes_params[id], score])


# creating gui calendar
class CustomDateEntry(DateEntry):
    def _select(self, event=None):
        date = self._calendar.selection_get()
        if date is not None:
            self._set_text(date.strftime('%d/%m/%Y'))
            self.event_generate('<<DateEntrySelected>>')
        self._top_cal.withdraw()
        if 'readonly' not in self.state():
            self.focus_set()


def open_calendar():
    calendar_root = Tk()
    # Add Calendar
    calendar_root.geometry("400x400")

    # Add Calendar
    cal = Calendar(calendar_root, selectmode='month',
                   year=datetime.today().year, month=datetime.today().month,
                   day=datetime.today().day)

    cal.pack(pady=20)

    def grad_date():
        date.config(text="Selected Date is: " + cal.get_date())

    # Add Button and Label
    Button(calendar_root, text="Get Date",
           command=grad_date).pack(pady=20)

    date = Label(calendar_root, text="")
    date.pack(pady=20)

    # Excecute Tkinter
    calendar_root.mainloop()


# running the search over the parameters given by the user
def run_search(source, dest, date, h, m, root):
    min_dist_source = {}
    min_dist_dest = {}
    time_start = datetime.strptime(str(h) + ":" + str(m), "%H:%M")
    # find the coordinates for the given address
    source_point = get_address_landmark(source)
    dest_point = get_address_landmark(dest)

    # going through all stops to find the closest to the coordinates
    for key_stop, val_stop in stop_2_stop.items():
        d = get_route_distance([source_point, (val_stop.lat, val_stop.lon)])
        min_dist_source[key_stop] = d
        d = get_route_distance([dest_point, (val_stop.lat, val_stop.lon)])
        min_dist_dest[key_stop] = d

    # sort the stops by distance
    a = dict(sorted(min_dist_source.items(), key=lambda item: item[1]))
    b = dict(sorted(min_dist_dest.items(), key=lambda item: item[1]))

    routes = {}
    all_routes_params = []
    dist_to_station = {}
    # find all the routes going from the source to destination
    for station_source, station_dest in itertools.product(list(a.items())[:5], list(b.items())[:5]):
        routes[station_source[0], station_dest[0]] = stop_to_stop_way(station_source[0], station_dest[0], time_start,
                                                                      datetime.strptime(str(date), "%d/%m/%Y"),
                                                                      timedelta(minutes=30), 1)
    model = create_score_route_model(8, "model.pth")
    bus_stations_ids = []
    walking_distance = []
    bus_ids = []
    time_arrival = []
    ride_time = []
    elevation_avg = []
    elevation_max = []
    # going through all routes
    for bus_route_key in list(routes.keys()):
        bus_route_key_val = routes[bus_route_key]
        if len(bus_route_key_val[0]) or len(bus_route_key_val[1]):
            if (source_point, bus_route_key[0]) not in dist_to_station:
                # getting the coordinates for the walking part of the route and distance
                dist_source = get_route(source_point,
                                        (stop_2_stop[bus_route_key[0]].lat, stop_2_stop[bus_route_key[0]].lon), 'foot')
                dist_to_station[(source_point, bus_route_key[0])] = [get_elevation(dist_source), dist_source]
                dist_source = dist_to_station[(source_point, bus_route_key[0])]
            if (bus_route_key[1], dest_point) not in dist_to_station:
                dist_dest = get_route((stop_2_stop[bus_route_key[1]].lat, stop_2_stop[bus_route_key[1]].lon),
                                      dest_point, 'foot')
                dist_to_station[(bus_route_key[1], dest_point)] = [get_elevation(dist_dest), dist_dest]
                dist_dest = dist_to_station[(bus_route_key[1], dest_point)]
            incline_parameters, _ = route_incline_parameters(dist_source[0] + dist_dest[0], dist_source[1],
                                                             dist_dest[1])
            # creating data for the NN
            if len(bus_route_key_val[1]):
                all_routes_params.append([get_route_distance(dist_source[1]) + get_route_distance(dist_dest[1]),
                                          (bus_route_key_val[1][2][2] + bus_route_key_val[1][4][2]).seconds,
                                          1,
                                          bus_route_key_val[1][2][3] + bus_route_key_val[1][4][3]] + incline_parameters)

                # creating data for the gui
                bus_stations_ids.append(
                    [stop_2_stop[bus_route_key[0]].stop_code, stop_2_stop[bus_route_key_val[1][0]].stop_code,
                     stop_2_stop[bus_route_key[1]].stop_code])
                walking_distance.append([get_route_distance(dist_source[1]), get_route_distance(dist_dest[1])])
                bus_ids.append([bus_route_key_val[1][1], bus_route_key_val[1][3]])
                time_arrival.append([bus_route_key_val[1][2][1], bus_route_key_val[1][4][1]])
                ride_time.append(bus_route_key_val[1][2][2] + bus_route_key_val[1][4][2])
                elevation_avg.append(incline_parameters[0])
                elevation_max.append(incline_parameters[1])

            # The same for direct routes
            if len(bus_route_key_val[0]):
                for one_trip_key, one_trip_val in bus_route_key_val[0].items():
                    all_routes_params.append([get_route_distance(dist_source[1]) + get_route_distance(dist_dest[1]),
                                              one_trip_val[2].seconds,
                                              0, one_trip_val[3]] + incline_parameters)
                    bus_stations_ids.append(
                        [stop_2_stop[bus_route_key[0]].stop_code,
                         stop_2_stop[bus_route_key[1]].stop_code])
                    walking_distance.append([get_route_distance(dist_source[1]), get_route_distance(dist_dest[1])])
                    bus_ids.append(one_trip_key)
                    time_arrival.append(one_trip_val[1] + one_trip_val[2])
                    ride_time.append(one_trip_val[2])
                    elevation_avg.append(incline_parameters[0])
                    elevation_max.append(incline_parameters[1])
        else:
            del routes[bus_route_key]

    # predict and sort by prediction
    if all_routes_params:
        score = model.predict(all_routes_params)
        indexes = np.argsort(score.squeeze())

        # run the results in a new window
        tk_2 = Toplevel()
        row_bus = RowRouteContainer(tk_2)
        row_bus.populate(np.array(bus_stations_ids)[indexes], np.round(np.array(walking_distance)[indexes], 2),
                         np.array(bus_ids)[indexes],
                         np.array(time_arrival)[indexes], np.array(ride_time)[indexes],
                         np.round(np.array(elevation_max)[indexes], 2),
                         np.round(np.array(elevation_avg)[indexes], 2))
        row_bus.grid(column=0, sticky='e', columnspan=4)
        feedback_botton = Button(tk_2, text="feedback",
                                 command=lambda: open_feedback(np.array(all_routes_params)[indexes]))
        feedback_botton.grid()
        tk_2.mainloop()
    else:
        messagebox.showinfo("No Routes", "There are no routes for these parameters")


# main window gui
root = Tk()
root.geometry("300x122")

# From Label + Entry
label_from = Label(root, text="From:", anchor=W)
label_from.grid(column=0, row=0, sticky=W, pady=5)

entry_from = Entry(root, bd=5, width=30)
entry_from.insert(0, "גלבוע 28 חיפה ישראל")
entry_from.grid(column=1, row=0, stick=EW, pady=5)

# To: Label + Entry
label_to = Label(root, text="To:", anchor=W)
label_to.grid(column=0, row=1, sticky=W, pady=5)

entry_to = Entry(root, bd=5)
entry_to.insert(0, "שדרות הנשיא,131,חיפה,ישראל")
entry_to.grid(column=1, row=1, stick=EW, pady=5)

# Flip button + loading PhotoImage
photo = PhotoImage(file=r"download.png")
photoimage = photo.subsample(10, 10)

flip_button = Button(root, image=photoimage, command=lambda: flip_address(entry_from, entry_to))
flip_button.grid(column=3, row=0, rowspan=2, padx=5, pady=5)

# Frame Container
f = Frame(root)
f.pack_propagate(0)
date_label = Label(f, text="Date:")
date_label.grid(column=0, row=0, sticky=W, padx=5)
time_label = Label(f, text="time:")
time_label.grid(column=1, row=0, sticky=W, padx=5)
entry = CustomDateEntry(f, width=12, background='darkblue',
                        foreground='white', borderwidth=2)
entry._set_text(entry._date.strftime('%d/%m/%Y'))

entry.grid(column=0, row=1, sticky=E, padx=5)
h_val_inside = StringVar(f)
h_val_inside.set(datetime.today().hour)
combo_hour = ttk.Combobox(f, values=list(range(0, 24)), width=3)
combo_hour.current(datetime.today().hour)
combo_hour.grid(column=1, row=1, sticky=E, padx=5)
combo_min = ttk.Combobox(f, values=list(range(0, 60)), width=3)
combo_min.current(datetime.today().minute)
combo_min.grid(column=2, row=1, sticky=E, padx=5)
search_button = Button(f, text="Search", width=10,
                       command=lambda: run_search(entry_from.get(), entry_to.get(), entry.get(), combo_hour.get(),
                                                  combo_min.get(), root))
search_button.grid(column=3, row=1, sticky=E, padx=5)
f.grid(column=0, row=4, columnspan=4)

root.title('Accessible Transport')
root.mainloop()
