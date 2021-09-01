from tkinter import *
from tkinter import ttk


class feedback_window(object):

    def __init__(self):
        self.q6 = IntVar()
        self.q5 = IntVar()
        self.q4 = IntVar()
        self.q3 = IntVar()
        self.q2 = IntVar()
        self.q1 = IntVar()
        self.q7 = IntVar()
        self.score = 0
        self.id_route = StringVar()

    def save_info(self, root):
        # root = Tk()
        q1_info = self.q1.get()
        q2_info = self.q2.get()
        q3_info = self.q3.get()
        q4_info = self.q4.get()
        q5_info = self.q5.get()
        q6_info = self.q6.get()
        q7_info = self.q7.get()
        # id_route = self.id.get()
        self.score = sum([q1_info, q2_info, q3_info, q4_info, q5_info, q6_info, q7_info]) / 7
        thank_you_window = Tk()
        Button(thank_you_window, text="Thank you", command=lambda: self.destroy_all(thank_you_window, root)).pack()

    def destroy_all(self, thank_you_window, root):
        thank_you_window.destroy()
        root.destroy()

    def main_frame(self, root):
        root.geometry("450x300")

        root.title('Feedback - How satisfied you are with:')

        label_id = Label(root, text="What Route ID did you choose?")
        label_id.grid(column=0, row=0, sticky=W, pady=5)

        entry_id = Entry(root,textvariable=self.id_route)
        entry_id.grid(column=1, row=0, sticky=W, pady=5)

        label_q1 = Label(root, text="The number of stops?")
        label_q1.grid(column=0, row=1, sticky=W, pady=5)

        combo_hour1 = ttk.Combobox(root, textvariable=self.q1, values=list(range(1, 6)))
        combo_hour1.grid(column=1, row=1, sticky=W, pady=5, columnspan=1)

        label_q2 = Label(root, text="The line arrival times?")
        label_q2.grid(column=0, row=2, sticky=W, pady=5)

        combo_hour2 = ttk.Combobox(root, textvariable=self.q2, values=list(range(1, 6)))
        combo_hour2.grid(column=1, row=2, sticky=W, pady=5, columnspan=1)

        label_q3 = Label(root, text="the distance of the station from the starting point?")
        label_q3.grid(column=0, row=3, sticky=W, pady=5)

        combo_hour2 = ttk.Combobox(root, textvariable=self.q3, values=list(range(1, 6)))
        combo_hour2.grid(column=1, row=3, sticky=W, pady=5, columnspan=1)

        label_q4 = Label(root, text="the distance to the destination from the station?")
        label_q4.grid(column=0, row=4, sticky=W, pady=5)

        combo_hour2 = ttk.Combobox(root, textvariable=self.q4, values=list(range(1, 6)))
        combo_hour2.grid(column=1, row=4, sticky=W, pady=5, columnspan=1)

        label_q5 = Label(root, text="the slope of the route?")
        label_q5.grid(column=0, row=5, sticky=W, pady=5)

        combo_hour2 = ttk.Combobox(root, textvariable=self.q5, values=list(range(1, 6)))
        combo_hour2.grid(column=1, row=5, sticky=W, pady=5, columnspan=1)

        label_q6 = Label(root, text="the length of the route?")
        label_q6.grid(column=0, row=6, sticky=W, pady=5)

        combo_hour2 = ttk.Combobox(root, textvariable=self.q6, values=list(range(1, 6)))
        combo_hour2.grid(column=1, row=6, sticky=W, pady=5, columnspan=1)

        label_q7 = Label(root, text="the route safety?")
        label_q7.grid(column=0, row=7, sticky=W, pady=5)

        combo_hour2 = ttk.Combobox(root, textvariable=self.q7, values=list(range(1, 6)))
        combo_hour2.grid(column=1, row=7, sticky=W, pady=5, columnspan=1)

        button = Button(root, text="Submit", command=lambda: self.save_info(root))
        button.grid(column=1, row=8, sticky=W, pady=5)


def get_score_from_feedback():
    root = Tk()
    app = feedback_window()
    app.main_frame(root)
    root.mainloop()
    return app.score,int(app.id_route.get())

