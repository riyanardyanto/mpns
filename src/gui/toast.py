from ttkbootstrap.toast import ToastNotification


def create_toast(message: str, bootstyle: str) -> ToastNotification:
    toast = ToastNotification(
        title="Information",
        message=message,
        bootstyle=bootstyle,
        duration=3000,
        alert=True,
    )
    toast.show_toast()
