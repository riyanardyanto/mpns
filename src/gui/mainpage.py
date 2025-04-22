import ttkbootstrap as ttk
from ttkbootstrap import Progressbar
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import TableRow, Tableview
from ttkbootstrap.toast import ToastNotification

from src.utils.constants import TABLE_HEAD


class MainScreen(ttk.Frame):
    def __init__(self, master: ttk.Window) -> None:
        super().__init__(master, padding=(0, 10))

        self.loading_frame = ttk.Frame(
            master=self,
        )
        self.loading_frame.pack(
            side=TOP,
            fill=X,
            padx=0,
            pady=(0, 10),
        )

        self.content_frame = ttk.Frame(
            master=self,
        )
        self.content_frame.pack(
            side=TOP,
            fill=BOTH,
            expand=YES,
            anchor=N,
            padx=0,
            pady=0,
        )

        self.progressbar = Progressbar(
            self.loading_frame,
            mode="determinate",
            bootstyle="success",
            orient="horizontal",
        )
        self.progressbar.pack(
            padx=(10, 0), pady=(0, 0), fill="x", side=LEFT, expand=YES
        )

        self.time_period = ttk.Label(
            master=self.loading_frame,
            text="",
            justify=RIGHT,
            # width=40,
        )
        self.time_period.pack(padx=(5, 10), pady=(0, 0), fill="none", side=RIGHT)

        self.table = Tableview(
            master=self.content_frame,
            coldata=TABLE_HEAD,
            rowdata=[],
            paginated=False,
            searchable=True,
            bootstyle=DARK,
            autofit=True,
            height=20,
        )
        self.table.pack(
            side=LEFT,
            fill=BOTH,
            anchor=W,
            expand=NO,
            padx=10,
            pady=0,
        )
        self.table.view.bind(
            sequence="<Double-1>",
            func=self.on_double_click,
        )

        ttk.Separator(
            self.content_frame,
            orient="vertical",
            style="success.Vertical.TSeparator",
        ).pack(side=LEFT, expand=NO, fill=Y, anchor=W)

        self.inp = ttk.ScrolledText(
            master=self.content_frame,
            # width=60,
            # height=32,
            font=("Consolas", 10),
            wrap=WORD,
        )
        self.inp.pack(
            side=LEFT,
            padx=10,
            pady=(0, 0),
            expand=YES,
            anchor=W,
            fill=BOTH,
        )

    def on_double_click(self, event):
        try:
            selected = self.table.view.selection()
            records = []
            for iid in selected:
                record: TableRow = self.table.iidmap.get(iid)
                records.append(record.values)
            msg = records[0][1]
            self.inp.insert(ttk.END, f"*{msg}*\n> \n\n")
        except Exception as e:
            toast = ToastNotification(
                title="Error",
                message=e,
                bootstyle=DANGER,
                duration=3000,
                alert=True,
            )
            toast.show_toast()
