from tkinter import ttk

import ttkbootstrap as ttk
from PIL import Image, ImageTk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from ttkwidgets.autocomplete import AutocompleteCombobox

from src.utils.helpers import resource_path


class Sidebar(ttk.Frame):
    def __init__(self, master: ttk.Frame):
        super().__init__(master, padding=(10, 10))
        self.home_frame = master
        self.select_shift = ttk.StringVar()
        self.photo = ImageTk.PhotoImage(
            image=Image.open(resource_path("assets/c5_spa.ico")).resize((80, 80))
        )

        # create left frame of window App
        L_frame = ttk.Frame(self.home_frame)
        L_frame.pack(side=LEFT, expand=NO, padx=10, pady=10, anchor=N)

        self.logo = ttk.Label(master=L_frame, image=self.photo)
        self.logo.pack(side=TOP, padx=10, pady=10)

        ttk.Separator(
            master=L_frame,
            orient="horizontal",
            style="danger.Horizontal.TSeparator",
        ).pack(side=TOP, expand=YES, fill=X, padx=0, pady=10)

        # create link up combo box
        link_up = ["LU18", "LU21", "LU26", "LU27"]
        self.lu = ttk.Combobox(
            L_frame,
            bootstyle="success",
            values=link_up,
            width=12,
            cursor="hand2",
        )
        self.lu.current(0)
        self.lu.pack(side=TOP, padx=10, pady=(10, 10))

        # create date entry
        self.dt = ttk.DateEntry(
            L_frame,
            bootstyle=SUCCESS,
            width=10,
            dateformat=r"%Y-%m-%d",
            cursor="hand2",
        )
        self.dt.pack(side=TOP, padx=10, pady=10)

        # create radio button select shift
        shifts = ["Shift 1", "Shift 2", "Shift 3"]
        for shift in shifts:
            ttk.Radiobutton(
                L_frame,
                bootstyle=SUCCESS,
                variable=self.select_shift,
                text=shift,
                value=shift,
                cursor="hand2",
            ).pack(padx=10, pady=5, anchor=W)

        # create get data button
        self.btn_get_data = ttk.Button(
            master=L_frame,
            text="Get Data",
            bootstyle=SUCCESS,
            width=13,
            cursor="hand2",
        )
        self.btn_get_data.pack(side=TOP, padx=10, pady=(10, 10))

        self.btn_result = ttk.Button(
            master=L_frame,
            text="Result",
            # command=self.result,
            bootstyle=SUCCESS,
            width=13,
            cursor="hand2",
        )
        self.btn_result.pack(
            side=TOP,
            padx=10,
            pady=(10, 10),
        )

        ttk.Separator(
            master=L_frame,
            orient="horizontal",
            style="danger.Horizontal.TSeparator",
        ).pack(
            side=TOP,
            expand=YES,
            fill=X,
            padx=0,
            pady=10,
        )

        # create qr code button
        self.btn_qr = ttk.Button(
            master=L_frame,
            text="QR Code",
            # command=self.show_qr,
            bootstyle=WARNING,
            width=13,
            cursor="hand2",
        )
        self.btn_qr.pack(
            side=TOP,
            padx=10,
            pady=(10, 10),
        )

        self.btn_target = ttk.Button(
            master=L_frame,
            text="Update Target",
            # command=self.save_excel,
            bootstyle=WARNING,
            width=13,
            cursor="hand2",
        )
        self.btn_target.pack(side=TOP, padx=10, pady=(10, 10))

        # create qr code button

        ttk.Separator(
            master=L_frame,
            orient="horizontal",
            style="danger.Horizontal.TSeparator",
        ).pack(
            side=TOP,
            expand=YES,
            fill=X,
            padx=0,
            pady=10,
        )

        # create username entry
        self.entry_user = AutocompleteCombobox(
            master=L_frame,
            width=12,
            # completevalues=model.get_data_from_excel(sheet_index=1),
            cursor="hand2",
        )
        self.entry_user.pack(
            side=TOP,
            padx=10,
            pady=(10, 10),
        )

        # create save to excel button
        self.btn_save = ttk.Button(
            master=L_frame,
            text="Save Excel",
            # command=self.save_excel,
            bootstyle=PRIMARY,
            width=13,
        )
        self.btn_save.pack(side=TOP, padx=10, pady=(10, 10))

        ttk.Separator(
            master=L_frame,
            orient="horizontal",
            style="danger.Horizontal.TSeparator",
        ).pack(
            side=TOP,
            expand=YES,
            fill=X,
            padx=0,
            pady=10,
        )

        ToolTip(self.btn_get_data, "Get data stop reason from SPA", delay=0)
        ToolTip(self.btn_result, "Show Target and Actual Result", delay=0)
        ToolTip(self.btn_qr, "Generate QR Code", delay=0)
        ToolTip(self.btn_target, "Open Target Editor", delay=0)
        ToolTip(self.btn_save, "Save to Excel", delay=0)
        ToolTip(self.entry_user, "Select Username", delay=0)
        ToolTip(self.lu, "Select Link Up", delay=0)
        ToolTip(self.dt, "Select Date", delay=0)
