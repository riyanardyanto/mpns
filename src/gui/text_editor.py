import tkinter as tk

import ttkbootstrap as ttk
from ttkbootstrap import Menu


class TextEditor(ttk.ScrolledText):
    def __init__(self, parent) -> None:
        super().__init__(parent, wrap=ttk.WORD, font=("Cascadia Code", 9))
        self.root = parent

        self.pack(
            side=tk.LEFT, padx=10, pady=(0, 0), expand=tk.YES, anchor=tk.W, fill=tk.BOTH
        )

        # Create context menu
        self.selected_menu: Menu = Menu(self.root, tearoff=0)
        self.selected_menu.add_command(
            label="Bold",
            command=self.bold_text,
            font=("Cascadia Code", 9, "bold"),
        )
        self.selected_menu.add_command(
            label="Italic",
            command=self.italic_text,
            font=("Cascadia Code", 9, "italic"),
        )
        self.selected_menu.add_command(
            label="Strikethrough",
            command=self.strikethrough_text,
            font=("Cascadia Code", 9, "overstrike"),
        )

        self.unselected_menu = Menu(self.root, tearoff=0)
        self.unselected_menu.add_command(label="Insert (>)", command=self.insert_desc)
        self.unselected_menu.add_command(label="Insert (-)", command=self.insert_list)

        # Bind right-click to show context menu
        self.bind("<Button-3>", self.show_context_menu)
        # if self.tag_ranges(ttk.SEL):
        self.bind("<Control-b>", lambda e: self.bold_text())
        self.bind("<Control-i>", lambda e: self.italic_text())

    def show_context_menu(self, event):
        # Only show menu if text is selected
        if self.tag_ranges(ttk.SEL):
            self.selected_menu.post(event.x_root, event.y_root)
        else:
            self.unselected_menu.post(event.x_root, event.y_root)

    def bold_text(self):
        try:
            selected_text = self.get(ttk.SEL_FIRST, ttk.SEL_LAST)
            if selected_text.startswith("*") and selected_text.endswith("*"):
                new_text = selected_text.strip("*")
            else:
                new_text = f"*{selected_text}*"
            self.delete(ttk.SEL_FIRST, ttk.SEL_LAST)
            self.insert(ttk.INSERT, new_text)

            # Check if the selected text has the "bold" tag
            # if "bold" in self.tag_names(ttk.SEL_FIRST):
            #     self.tag_remove("bold", ttk.SEL_FIRST, ttk.SEL_LAST)
            # else:
            #     self.tag_add("bold", ttk.SEL_FIRST, ttk.SEL_LAST)
            #     self.tag_configure("bold", font=("Cascadia Code", 9, "bold"))

        except tk.TclError:
            pass

    def italic_text(self):
        try:
            selected_text = self.get(ttk.SEL_FIRST, ttk.SEL_LAST)
            if selected_text.startswith("_") and selected_text.endswith("_"):
                self.delete(ttk.SEL_FIRST, ttk.SEL_LAST)
                self.insert(ttk.INSERT, selected_text.strip("_"))
            else:
                self.delete(ttk.SEL_FIRST, ttk.SEL_LAST)
                self.insert(ttk.INSERT, f"_{selected_text}_")

            # if "italic" in self.tag_names(ttk.SEL_FIRST):
            #     self.tag_remove("italic", ttk.SEL_FIRST, ttk.SEL_LAST)
            #     self.tag_configure("italic", font=("Cascadia Code", 9, "normal"))
            # else:
            #     self.tag_add("italic", ttk.SEL_FIRST, ttk.SEL_LAST)
            #     self.tag_configure("italic", font=("Cascadia Code", 9, "italic"))
        except tk.TclError:
            pass

    def strikethrough_text(self):
        try:
            first, last = ttk.SEL_FIRST, ttk.SEL_LAST
            selected_text = self.get(first, last)
            if selected_text.startswith("~") and selected_text.endswith("~"):
                new_text = selected_text[1:-1]
            else:
                new_text = f"~{selected_text}~"
            self.delete(first, last)
            self.insert(ttk.INSERT, new_text)

            # if "strikethrough" in self.tag_names(first):
            #     self.tag_remove("strikethrough", first, last)
            #     self.tag_configure("strikethrough", font=("Cascadia Code", 9, "normal"))
            # else:
            #     self.tag_add("strikethrough", first, last)
            #     self.tag_configure(
            #         "strikethrough", font=("Cascadia Code", 9, "overstrike")
            #     )
        except tk.TclError:
            pass

    def inline_text(self):
        try:
            selected_text = self.get(ttk.SEL_FIRST, ttk.SEL_LAST)
            self.delete(ttk.SEL_FIRST, ttk.SEL_LAST)

            self.insert(ttk.INSERT, f"{self.add_combining_chars(selected_text)}")
        except tk.TclError:
            pass

    def insert_desc(self):
        try:
            cursor_pos = self.index(tk.INSERT)
            if cursor_pos.split(".")[1] == "0":
                # If the cursor is at the start of the text, insert at the beginning
                self.insert(ttk.INSERT, "> ")
            else:
                # Otherwise, insert at the current cursor position
                self.insert(ttk.INSERT, "\n> ")

        except tk.TclError:
            pass

    def insert_list(self):
        try:
            cursor_pos = self.index(tk.INSERT)
            if cursor_pos.split(".")[1] == "0":
                # If the cursor is at the start of the text, insert at the beginning
                self.insert(ttk.INSERT, "- ")
            else:
                # Otherwise, insert at the current cursor position
                self.insert(ttk.INSERT, "\n- ")
        except tk.TclError:
            pass

    def add_combining_chars(self, text):
        # Unicode for combining double macron (U+035E) and double low line (U+035F)
        combining_chars = "\u035e\u035f"
        # Use join to insert combining characters after each character
        return "".join(char + combining_chars for char in text)
