from async_tkinter_loop import async_mainloop

from src import View


def main():
    app = View()
    async_mainloop(app)


if __name__ == "__main__":
    main()
