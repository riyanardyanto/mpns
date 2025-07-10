import tkinter as tk
from tkinter import filedialog

import pandas as pd
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip

from src.gui.toast import create_toast


class EditableTableview(ttk.Frame):
    def __init__(self, parent, columns, data=None, col_tittle: str = None):
        super().__init__(parent)

        # Custom index values
        self.index_values = ["STOP", "PR", "MTBF", "UPDT", "PDT", "NATR"]

        # Add 'Index' column with custom values
        self.columns = [col_tittle] + list(columns)
        self.original_columns = columns  # Store original columns without 'Index'

        # Configure Treeview style
        self.style = ttk.Style()
        self.style.configure(
            "Custom.Treeview",
            rowheight=25,
            fieldbackground="#f0f0f0",
        )
        self.style.configure("Custom.Treeview.Heading", anchor="center")

        # Create Treeview widget
        self.treeview = ttk.Treeview(
            self,
            columns=self.columns,
            show="headings",
            style="Custom.Treeview",
            selectmode="extended",
            bootstyle=PRIMARY,
            height=6,
        )

        # Setup columns
        self._setup_columns()

        # Add data if provided
        if data is not None:
            self._populate_data(data)

        # Bind events
        self.treeview.bind("<Double-1>", self.on_double_click)
        self.treeview.bind("<Control-v>", self.paste_from_clipboard)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=scrollbar.set)

        # Layout
        self.treeview.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Entry widget for editing
        self.entry = ttk.Entry(self, bootstyle=INFO)
        self.entry.editing_item = None
        self.entry.editing_column = None

        ToolTip(self.treeview, text="Double click to edit", delay=0)

    def _setup_columns(self):
        """Setup Treeview columns and headings."""
        for col in self.columns:
            self.treeview.heading(col, text=col, anchor="center")
            width = 100 if col == "Index" else 120  # Adjust column width
            self.treeview.column(col, width=width, anchor="center", stretch=True)

    def _populate_data(self, data):
        """Populate Treeview with initial data."""
        for i, item in enumerate(data):
            index_val = (
                self.index_values[i] if i < len(self.index_values) else str(i + 1)
            )
            self.treeview.insert("", END, values=(index_val,) + tuple(item))

    def on_double_click(self, event):
        """Handle double-click events for editing cells."""
        region = self.treeview.identify_region(event.x, event.y)
        if region == "cell":
            column = self.treeview.identify_column(event.x)
            item = self.treeview.focus()

            col_index = int(column[1:]) - 1
            if col_index == 0:  # Skip editing for 'Index' column
                return

            current_value = self.treeview.item(item, "values")[col_index]
            x, y, width, height = self.treeview.bbox(item, column)

            self.entry.editing_item = item
            self.entry.editing_column = col_index
            self.entry.place(x=x, y=y, width=width, height=height)
            self.entry.delete(0, END)
            self.entry.insert(0, current_value)
            self.entry.focus()

            self.entry.bind("<Return>", self.accept_edit)
            self.entry.bind("<Escape>", self.cancel_edit)
            self.entry.bind("<FocusOut>", self.accept_edit)

    def accept_edit(self, event=None):
        """Accept the edit and update the Treeview."""
        if self.entry.editing_item and self.entry.editing_column is not None:
            new_value = self.entry.get()
            values = list(self.treeview.item(self.entry.editing_item, "values"))
            values[self.entry.editing_column] = new_value
            self.treeview.item(self.entry.editing_item, values=values)
        self.cancel_edit()

    def cancel_edit(self, event=None):
        """Cancel the edit and hide the entry widget."""
        self.entry.place_forget()
        self.entry.editing_item = None
        self.entry.editing_column = None

    def paste_from_clipboard(self, event):
        """Paste data from the clipboard into the Treeview."""
        try:
            clipboard_data = self.clipboard_get()
            rows = clipboard_data.split("\n")
            data = [row.split("\t") for row in rows if row.strip()]

            selected_items = self.treeview.selection()
            if not selected_items:
                selected_items = [
                    self.treeview.focus() or self.treeview.get_children()[0]
                ]

            start_index = self.treeview.index(selected_items[0])

            for i, row in enumerate(data):
                if start_index + i < len(self.treeview.get_children()):
                    item = self.treeview.get_children()[start_index + i]
                    current_values = list(self.treeview.item(item, "values"))
                    for j, value in enumerate(row):
                        if j < len(self.original_columns):
                            current_values[j + 1] = value
                    self.treeview.item(item, values=current_values)
                else:
                    index_num = start_index + i
                    index_val = (
                        self.index_values[index_num]
                        if index_num < len(self.index_values)
                        else str(index_num + 1)
                    )
                    self.treeview.insert(
                        "",
                        END,
                        values=(index_val,) + tuple(row[: len(self.original_columns)]),
                    )
        except tk.TclError:
            create_toast("No data in clipboard", WARNING)

    def get_data(self):
        """Return all data from the table as a list of tuples (excluding 'Index' column)."""
        return [
            self.treeview.item(item, "values")[1:]
            for item in self.treeview.get_children()
        ]

    def load_from_dataframe(self, df):
        """Load data from a pandas DataFrame."""
        self.treeview.delete(*self.treeview.get_children())
        for i, (_, row) in enumerate(df.iterrows()):
            index_val = (
                self.index_values[i] if i < len(self.index_values) else str(i + 1)
            )
            self.treeview.insert("", END, values=(index_val,) + tuple(row))

    def save_to_csv(self, filename=None):
        """
        Save data from the Treeview to a CSV file.
        If no filename is provided, prompt the user to select a file.
        """
        if not filename:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            )
        if not filename:
            return False

        data = self.get_data()
        columns = self.original_columns

        try:
            df = pd.DataFrame(data, columns=columns)
            df.to_csv(filename, index=False)
            create_toast(f"Data successfully saved: {filename}", SUCCESS)
            return True
        except Exception as e:
            create_toast(f"Failed to save file: {str(e)}", DANGER)
            return False
