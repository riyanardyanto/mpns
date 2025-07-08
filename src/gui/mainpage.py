import ttkbootstrap as ttk
from ttkbootstrap import Progressbar
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import TableRow, Tableview
from ttkbootstrap.toast import ToastNotification

from src.gui.text_editor import TextEditor
from src.utils.constants import TABLE_HEAD


class MainScreen(ttk.Frame):
    def __init__(self, master: ttk.Window) -> None:
        super().__init__(master, padding=(0, 10))

        # Create the loading frame (progress bar and time period label)
        self._create_loading_frame()

        # Create the content frame (table and text area)
        self._create_content_frame()

    def _create_loading_frame(self):
        """Create the loading frame with a progress bar and time period label."""
        self.loading_frame = ttk.Frame(master=self)
        self.loading_frame.pack(side=TOP, fill=X, padx=0, pady=(0, 10))

        # Progress bar
        self.progressbar = Progressbar(
            self.loading_frame,
            mode="determinate",
            bootstyle="success",
            orient="horizontal",
        )
        self.progressbar.pack(
            padx=(10, 0), pady=(0, 0), fill="x", side=LEFT, expand=YES
        )

        # Time period label
        self.time_period = ttk.Label(
            master=self.loading_frame,
            text="",
            justify=RIGHT,
        )
        self.time_period.pack(padx=(5, 10), pady=(0, 0), fill="none", side=RIGHT)

    def _create_content_frame(self):
        """Create the content frame with a table and a text area."""
        self.content_frame = ttk.Frame(master=self)
        self.content_frame.pack(
            side=TOP, fill=BOTH, expand=YES, anchor=N, padx=0, pady=0
        )

        # Table for displaying data
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
        self.table.pack(side=LEFT, fill=BOTH, anchor=W, expand=NO, padx=10, pady=0)
        self.table.view.bind(sequence="<Double-1>", func=self.on_double_click)

        # Vertical separator between table and text area
        ttk.Separator(
            self.content_frame,
            orient="vertical",
            style="success.Vertical.TSeparator",
        ).pack(side=LEFT, expand=NO, fill=Y, anchor=W)

        # Text area for displaying detailed information
        # self.inp = ttk.ScrolledText(
        #     master=self.content_frame,
        #     font=("Consolas", 10),
        #     wrap=WORD,
        # )
        self.inp = TextEditor(self.content_frame)
        # self.inp.pack(side=LEFT, padx=10, pady=(0, 0), expand=YES, anchor=W, fill=BOTH)

    def on_double_click(self, event):
        """Handle double-click events on the table rows."""
        try:
            selected = self.table.view.selection()
            records = []
            for iid in selected:
                record: TableRow = self.table.iidmap.get(iid)
                records.append(record.values)

            if records:
                msg = records[0][1]  # Assuming the second column contains the message
                self.inp.insert(ttk.END, f"*{msg}*\n> \n\n")
            else:
                raise ValueError("No record selected.")
        except Exception as e:
            # Display an error notification
            toast = ToastNotification(
                title="Error",
                message=f"An error occurred: {e}",
                bootstyle=DANGER,
                duration=3000,
                alert=True,
            )
            toast.show_toast()
