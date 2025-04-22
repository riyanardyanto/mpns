import tkinter as tk
from tkinter import filedialog

import pandas as pd
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip

from src.gui.toast import create_toast


class EditableTableview(ttk.Frame):
    def __init__(self, parent, columns, data=None):
        super().__init__(parent)

        # Custom index values
        self.index_values = ["STOP", "PR", "MTBF", "UPDT", "PDT", "NATR"]

        # Tambahkan kolom 'Index' dengan custom values
        self.columns = ["Index"] + list(columns)
        self.original_columns = columns  # Simpan kolom asli tanpa index

        self.style = ttk.Style()
        self.style_name = f"CustomTreeview{30}.Treeview"
        self.style.configure(
            self.style_name,
            rowheight=25,
            # font=("roboto", 10, "normal"),
            # background="#f0f0f0",
            # foreground="#333333",
            fieldbackground="#f0f0f0",
            # bordercolor="#333333",
            # borderwidth=1,
            highlightthickness=0,
            highlightbackground="#333333",
            highlightcolor="#333333",
            # selectbackground="#333333",
            # selectforeground="#f0f0f0",
            # padding=5,
        )
        self.style.configure("Centered.Treeview", anchor="center")
        self.style.configure("Centered.Treeview.Heading", anchor="center")

        self.treeview = ttk.Treeview(
            self,
            columns=self.columns,
            show="headings",
            style=self.style_name,
            selectmode="extended",
            bootstyle=PRIMARY,
            height=6,
        )

        for col in columns:
            self.treeview.heading(col, text=col, anchor="center")
            self.treeview.column(col, anchor="center", stretch=True)

        # Setup columns
        for col in self.columns:
            self.treeview.heading(col, text=col)
            # Lebar kolom disesuaikan
            if col == "Index":
                width = 100  # Lebar lebih besar untuk custom index
            else:
                width = 100
            self.treeview.column(col, width=width, stretch=(col != "Index"))

        # Add data if provided
        if data is not None:
            for i, item in enumerate(data):
                # Gunakan custom index atau nomor urut jika data melebihi index_values
                index_val = (
                    self.index_values[i] if i < len(self.index_values) else str(i + 1)
                )
                self.treeview.insert("", END, values=(index_val,) + tuple(item))

        # Bind double click for editing (kecuali kolom Index)
        self.treeview.bind("<Double-1>", self.on_double_click)

        # Bind Ctrl+V for paste
        self.treeview.bind("<Control-v>", self.paste_from_clipboard)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=scrollbar.set)

        # Layout
        # self.treeview.grid(row=0, column=0, sticky="ns")
        # scrollbar.grid(row=0, column=1, sticky="ns")
        self.treeview.pack(side=LEFT, fill=BOTH, expand=True)
        # scrollbar.pack(side=RIGHT, fill=Y)

        # self.grid_rowconfigure(0, weight=1)
        # self.grid_columnconfigure(0, weight=1)

        # Entry widget for editing
        self.entry = ttk.Entry(self, bootstyle=INFO)
        self.entry.editing_item = None
        self.entry.editing_column = None

        ToolTip(self.treeview, text="Double click to edit", delay=0)

    def on_double_click(self, event):
        # Identify the item and column clicked
        region = self.treeview.identify_region(event.x, event.y)
        if region == "cell":
            column = self.treeview.identify_column(event.x)
            item = self.treeview.focus()

            # Get column index
            col_index = int(column[1:]) - 1

            # Skip editing jika kolom Index (index 0)
            if col_index == 0:
                return

            # Get current value
            current_value = self.treeview.item(item, "values")[col_index]

            # Get cell coordinates
            x, y, width, height = self.treeview.bbox(item, column)

            # Configure and place entry widget
            self.entry.editing_item = item
            self.entry.editing_column = col_index
            self.entry.place(x=x, y=y, width=width, height=height)
            self.entry.delete(0, END)
            self.entry.insert(0, current_value)
            self.entry.focus()

            # Bind Enter and Escape keys
            self.entry.bind("<Return>", self.accept_edit)
            self.entry.bind("<Escape>", self.cancel_edit)
            self.entry.bind("<FocusOut>", self.accept_edit)

    def accept_edit(self, event=None):
        if self.entry.editing_item and self.entry.editing_column is not None:
            # Get new value
            new_value = self.entry.get()

            # Get current values
            values = list(self.treeview.item(self.entry.editing_item, "values"))

            # Update the edited value
            values[self.entry.editing_column] = new_value

            # Update the item
            self.treeview.item(self.entry.editing_item, values=values)

        self.cancel_edit()

    def cancel_edit(self, event=None):
        self.entry.place_forget()
        self.entry.editing_item = None
        self.entry.editing_column = None

    def paste_from_clipboard(self, event):
        try:
            # Get clipboard data
            clipboard_data = self.clipboard_get()

            # Split into rows and columns
            rows = clipboard_data.split("\n")
            data = [row.split("\t") for row in rows if row.strip()]

            # Get selected items or start from focused item
            selected_items = self.treeview.selection()
            if not selected_items:
                selected_items = [
                    self.treeview.focus() or self.treeview.get_children()[0]
                ]

            # Find starting position
            # start_item = selected_items[0]
            # print(start_item)
            start_index = self.treeview.index("I001")

            # Insert or update data (skip kolom Index)
            for i, row in enumerate(data):
                if start_index + i < len(self.treeview.get_children()):
                    # Update existing row
                    item = self.treeview.get_children()[start_index + i]
                    current_values = list(self.treeview.item(item, "values"))

                    # Update only the columns that have data (mulai dari index 1)
                    for j, value in enumerate(row):
                        if j < len(self.original_columns):
                            current_values[j + 1] = value  # +1 untuk skip kolom Index

                    self.treeview.item(item, values=current_values)
                else:
                    # Add new row dengan custom index atau nomor urut
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
            # No data in clipboard
            pass

    def get_data(self):
        """Return all data from the table as a list of tuples (tanpa kolom Index)"""
        return [
            self.treeview.item(item, "values")[1:]
            for item in self.treeview.get_children()
        ]

    def load_from_dataframe(self, df):
        """Load data from a pandas DataFrame"""
        self.treeview.delete(*self.treeview.get_children())
        for i, (_, row) in enumerate(df.iterrows()):
            # Gunakan custom index atau nomor urut jika data melebihi index_values
            index_val = (
                self.index_values[i] if i < len(self.index_values) else str(i + 1)
            )
            self.treeview.insert("", END, values=(index_val,) + tuple(row))

    def save_to_csv(self, filename=None):
        """
        Menyimpan data dari Treeview ke file CSV
        Jika filename tidak diberikan, akan memunculkan dialog save file
        """
        data = self.get_data()
        columns = self.original_columns

        try:
            df = pd.DataFrame(data, columns=columns)
            df.to_csv(filename, index=False)
            create_toast(f"Data berhasil disimpan : {filename}", SUCCESS)

            return True
        except Exception as e:
            create_toast(f"Gagal menyimpan file: {str(e)}", DANGER)
            return False


# # Contoh penggunaan
# if __name__ == "__main__":
#     app = ttk.Window(themename="superhero")
#     app.title("Editable Tableview with Custom Index")

#     with open("assets/target_baru.csv", "r") as f:
#         df = pd.read_csv(f)

#     # print(df)

#     columns = df.columns.to_list()
#     data = df.values.tolist()

#     # columns = ["Shift 1", "Shift 2", "Shift 3"]
#     # data = [
#     #     ("3", "3", "3"),
#     #     ("65.0%", "69.2%", "77.5%"),
#     #     ("111", "117", "131"),
#     #     ("4.9%", "4.9%", "4.9%"),
#     #     ("26.0%", "21.8%", "13.5%"),
#     #     ("4.1%", "4.1%", "4.1%"),
#     # ]

#     table = EditableTableview(app, columns, data)
#     table.pack(fill=BOTH, expand=False, padx=10, pady=10)

#     # Tombol untuk menyimpan ke CSV
#     save_btn = ttk.Button(
#         app,
#         text="Simpan ke CSV",
#         command=lambda: table.save_to_csv(),
#         bootstyle=SUCCESS,
#     )
#     save_btn.pack(pady=5)

#     app.mainloop()
