import ttkbootstrap as ttk
from async_tkinter_loop import async_mainloop

from src import View, resource_path


def main():
    app = View()
    async_mainloop(app)


if __name__ == "__main__":
    main()
