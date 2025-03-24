import ttkbootstrap as ttk
from async_tkinter_loop import async_mainloop

from app import MPnSEngine, resource_path


def main():
    app = ttk.Window(
        title="File Search Engine",
        themename="superhero",
        iconphoto=resource_path("app/assets/pm.jpg"),
    )
    print(resource_path("app/assets/pm.jpg"))
    MPnSEngine(app)
    async_mainloop(app)


if __name__ == "__main__":
    main()
