import tkinter as tk
from tkinter import *

# creating a gui list that contains all routes
class RowRouteContainer(tk.Frame):
    def __init__(self, parent):

        tk.Frame.__init__(self, parent)
        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.frame = tk.Frame(self.canvas,height = 400,width =400, background="#ffffff")
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.vsb2 = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.vsb.set,xscrollcommand = self.vsb2.set)

        self.vsb.pack(side="right", fill="y")
        self.vsb2.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4,4), window=self.frame, anchor="nw",
                                  tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)


    def populate(self,bus_stations_ids,walking_distance,bus_ids,time_arrival,ride_time, elevation_max,elevation_avg):

        bus_pic = PhotoImage(file=r"bus_icon.png")
        bus_pic = bus_pic.subsample(15,15)
        station_pic = PhotoImage(file=r"station_icon.png")
        station_pic = station_pic.subsample(12, 12)
        clock_pic = PhotoImage(file=r"clock_icon.png")
        clock_pic = clock_pic.subsample(15, 15)
        walking_man_pic = PhotoImage(file=r"walkingman.png")
        walking_man_pic = walking_man_pic.subsample(10, 10)
        idx = 0
        for bus_id_idx,bus_id in enumerate(bus_ids):
            tk.Label(self.frame, text="%s" % (bus_id_idx+1), width=3, borderwidth="1",
                     relief="solid").grid(row=idx, column=0)
            img_l = tk.Label(self.frame,image=walking_man_pic)
            img_l.photo = walking_man_pic
            img_l.grid(row=idx, column=1)
            tk.Label(self.frame, text=str(walking_distance[bus_id_idx][0]) + " km").grid(row=idx, column=2)
            img_l = tk.Label(self.frame, image=station_pic)
            img_l.photo = station_pic
            img_l.grid(row=idx, column=3)

            if type(bus_id) == int:
                tk.Label(self.frame, text=str(bus_stations_ids[bus_id_idx][0])).grid(row=idx, column=4)
                img_l = tk.Label(self.frame, image=bus_pic)
                img_l.photo = bus_pic
                img_l.grid(row=idx, column=5)
                tk.Label(self.frame, text=str(bus_id)).grid(row=idx, column=6)

                img_l = tk.Label(self.frame, image=clock_pic)
                img_l.photo = clock_pic
                img_l.grid(row=idx, column=7)
                tk.Label(self.frame, text=time_arrival[bus_id_idx].strftime("%H:%M")).grid(row=idx, column=8)

                img_l = tk.Label(self.frame, image=station_pic)
                img_l.photo = station_pic
                img_l.grid(row=idx, column=9)
                tk.Label(self.frame, text=str(bus_stations_ids[bus_id_idx][1])).grid(row=idx, column=10)

                img_l = tk.Label(self.frame, image=walking_man_pic)
                img_l.photo = walking_man_pic
                img_l.grid(row=idx, column=11)
                tk.Label(self.frame, text=str(walking_distance[bus_id_idx][1]) + " km").grid(row=idx, column=12)

            else:
                tk.Label(self.frame, text=str(bus_stations_ids[bus_id_idx][0])).grid(row=idx, column=4)
                img_l = tk.Label(self.frame, image=bus_pic)
                img_l.photo = bus_pic
                img_l.grid(row=idx, column=5)
                tk.Label(self.frame, text=str(bus_id[0])).grid(row=idx, column=6)

                img_l = tk.Label(self.frame, image=clock_pic)
                img_l.photo = clock_pic
                img_l.grid(row=idx, column=7)
                tk.Label(self.frame, text=time_arrival[bus_id_idx][0].strftime("%H:%M")).grid(row=idx, column=8)

                img_l = tk.Label(self.frame, image=station_pic)
                img_l.photo = station_pic
                img_l.grid(row=idx, column=9)
                tk.Label(self.frame, text=str(bus_stations_ids[bus_id_idx][1])).grid(row=idx, column=10)


                img_l = tk.Label(self.frame, image=bus_pic)
                img_l.photo = bus_pic
                img_l.grid(row=idx, column=11)
                tk.Label(self.frame, text=str(bus_id[1])).grid(row=idx, column=12)

                img_l = tk.Label(self.frame, image=clock_pic)
                img_l.photo = clock_pic
                img_l.grid(row=idx, column=13)
                tk.Label(self.frame, text=time_arrival[bus_id_idx][1].strftime("%H:%M")).grid(row=idx, column=14)

                img_l = tk.Label(self.frame, image=station_pic)
                img_l.photo = station_pic
                img_l.grid(row=idx, column=15)
                tk.Label(self.frame, text=str(bus_stations_ids[bus_id_idx][2])).grid(row=idx, column=16)

                img_l = tk.Label(self.frame, image=walking_man_pic)
                img_l.photo = walking_man_pic
                img_l.grid(row=idx, column=17)
                tk.Label(self.frame, text=str(walking_distance[bus_id_idx][1]) + " km").grid(row=idx, column=18)

            tk.Label(self.frame, text="avg slope: "+str(elevation_avg[bus_id_idx])).grid(row=idx+1, column=0, columnspan=3)

            tk.Label(self.frame, text="max slope: " + str(elevation_max[bus_id_idx])).grid(row=idx + 1, column=3,
                                                                                              columnspan=3)

            tk.Label(self.frame, text="ride time: " + str(ride_time[bus_id_idx].total_seconds()//60)).grid(row=idx + 1, column=6,
                                                                                              columnspan=3)
            idx = idx+2


    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
