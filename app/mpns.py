import asyncio
import json
import os
import pathlib
import sys
from typing import Dict

import httpx
import pandas as pd
import ttkbootstrap as ttk
from async_tkinter_loop import async_handler
from PIL import Image, ImageTk
from ttkbootstrap import Progressbar
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import TableRow, Tableview
from ttkbootstrap.toast import ToastNotification


class MPnSEngine(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill=BOTH, expand=YES)

        # application variables
        self.data: Dict = get_data_settings()
        self.list_link_up = list(self.data["lu"])

        self.path_var = ttk.StringVar(value="")

        self.create_sidebar()
        self.create_mainpage()
        self.create_textpage()

    def create_sidebar(self):
        sidebar = ttk.Frame(self)
        sidebar.pack(fill=X, side=LEFT, expand=NO, anchor=NW, padx=(0, 0))

        self.photo = ImageTk.PhotoImage(
            image=Image.open(resource_path("app/assets/pm.ico")).resize((80, 80))
        )

        self.logo = ttk.Label(master=sidebar, image=self.photo)
        self.logo.pack(side=TOP, padx=5, pady=(15, 0), anchor=CENTER, expand=NO)

        self.lu = ttk.Combobox(
            sidebar,
            bootstyle="success",
            values=self.list_link_up,
            width=12,
            cursor="hand2",
        )
        self.lu.current(0)
        self.lu.pack(side=TOP, padx=10, pady=(20, 10))

        self.browse_btn = ttk.Button(
            master=sidebar,
            text="Browse",
            command=self.load_data,
            width=13,
        )
        self.browse_btn.pack(side=TOP, padx=5, pady=5, anchor=CENTER)

        search_btn = ttk.Button(
            master=sidebar,
            text="Load Excel",
            command=self.load_dataframe,
            bootstyle=OUTLINE,
            width=13,
        )
        search_btn.pack(side=TOP, padx=5, pady=5, anchor=CENTER)

    def create_mainpage(self):
        mainpage = ttk.Frame(self)
        mainpage.pack(fill=BOTH, expand=YES, side=LEFT, padx=5, pady=(0, 10))

        self.tableview = Tableview(
            master=mainpage,
            height=30,
            coldata=["DATE", "Shift", "Owner", "Tech.", "Activity Description"],
            autofit=True,
            searchable=True,
        )

        self.tableview.get_column(-1).configure(stretch=True, expand=True, autofit=True)
        self.tableview.view.bind(
            sequence="<Double-1>",
            func=self.on_double_click,
        )
        self.tableview.pack(fill=BOTH, expand=YES)

        self.progressbar = Progressbar(
            mainpage,
            mode="determinate",
            bootstyle="success",
            orient="horizontal",
        )

        self.text = ttk.Text(master=mainpage)
        # self.text.pack(fill=BOTH, expand=YES)

    def create_textpage(self):
        textpage = ttk.Frame(self)
        textpage.pack(fill=BOTH, expand=YES, side=LEFT, padx=(5, 10), pady=(10, 10))

        self.text = ttk.Text(
            master=textpage,
            wrap=WORD,
        )
        self.text.configure(font=("Consolas", 10))
        # self.text.insert(END, self.path_var.get())
        self.text.pack(fill=BOTH, expand=YES)

    @async_handler
    async def load_data(self):
        self.progressbar.start()
        self.progressbar.pack(padx=10, pady=10, fill="x")

        self.text.delete(1.0, END)
        self.text.insert(END, "Loading...")
        self.browse_btn.config(state=DISABLED)
        # label.pack_forget()

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(self.data["url"], follow_redirects=True)

            self.text.delete(1.0, END)

            self.text.insert(END, f"Status: {response.status_code}\n")
            self.text.insert(END, f"Content-type: {response.headers['content-type']}\n")

            html = response.text.replace("\r\n", "\n")
            self.text.insert(END, f"Body:\n{html[:1000]}...")
            self.progressbar.stop()
            self.progressbar.pack_forget()

            self.browse_btn.config(state=NORMAL)

    async def load_data_excel(
        self, filepath: pathlib.Path = "Book1.xlsx", sheet_name: str = "Sheet1"
    ) -> pd.DataFrame:
        """
        Asynchronous wrapper around pd.read_excel

        Args:
            filepath (Path): Path to the Excel file. Defaults to "Book1.xlsx".
            sheet_name (str): Sheet name to read. Defaults to "Sheet1".

        Returns:
            pd.DataFrame: DataFrame containing the read Excel sheet.
        """
        loop = asyncio.get_event_loop()
        df = await loop.run_in_executor(None, pd.read_excel, filepath, sheet_name)

        return df

    @async_handler
    async def load_dataframe(self):
        self.progressbar.pack(padx=10, pady=10, fill="x")
        self.progressbar.start()

        df = await self.load_data_excel(filepath=self.data["lu"][self.lu.get()])
        df = df.iloc[3:].dropna(axis=1, how="all")
        df.columns = df.iloc[0]
        df = df[1:]
        df["DATE"] = (
            pd.to_datetime(df["DATE"], errors="coerce")
            .dt.strftime("%Y-%m-%d")
            .astype(str)
        )

        new_df = df[["DATE", "Shift", "Owner", "Tech.", "Activity Description"]]
        new_df = new_df.dropna(subset=["Activity Description"]).sort_values("DATE")

        col = new_df.columns.to_list()
        row = new_df.values.tolist()

        self.tableview.build_table_data(col, row)
        self.tableview.reset_table()
        self.tableview.get_column(-1).configure(stretch=True, expand=True, autofit=True)

        self.progressbar.stop()
        self.progressbar.pack_forget()

    def on_double_click(self, event):
        try:
            selected = self.tableview.view.selection()
            records = []
            for iid in selected:
                record: TableRow = self.tableview.iidmap.get(iid)
                records.append(record.values)
            tanggal = records[0][0]
            shift = records[0][1]
            owner = records[0][2]
            tech = records[0][3]
            activity = records[0][4]
            msg = f"Tanggal: {tanggal}\nShift: {shift}\nOwner: {owner}\nTech: {tech}\nActivity: {activity}"
            self.text.insert(ttk.END, f"*{msg}*\n> \n\n")
        except Exception as e:
            toast = ToastNotification(
                title="Error",
                message=e,
                bootstyle=DANGER,
                duration=3000,
                alert=True,
            )
            toast.show_toast()


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller

    Args:
        relative_path: The relative path to the resource.

    Returns:
        str: The absolute path to the resource.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def get_script_folder() -> str:
    """Get absolute path to the script folder, works for dev and for PyInstaller

    When running as a PyInstaller bundle, sys.executable is the path to the
    executable. Otherwise, we get the path to the script that was executed.

    Returns:
        str: The absolute path to the script folder.
    """

    if getattr(sys, "frozen", False):
        script_path: str = os.path.dirname(sys.executable)
    else:
        script_path: str = os.path.dirname(
            os.path.abspath(sys.modules["__main__"].__file__)
        )
    return script_path


def get_data_settings():
    if not os.path.exists(resource_path("settings_app.json")):
        with open(resource_path("settings_app.json"), "w") as f:
            json.dump(
                {
                    "lu": {
                        "LU18": "",
                        "LU21": "",
                        "LU22": "",
                        "LU23": "",
                        "LU24": "",
                        "LU25": "",
                    },
                    "url": "https://dummyjson.com/products?sortBy=title&order=asc",
                    "username": "",
                    "password": "",
                    "user": [],
                },
                f,
            )
    with open(resource_path("settings_app.json"), "rb") as f:
        data = json.load(f)
    return data
