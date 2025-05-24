import qrcode
import ttkbootstrap as ttk
from PIL import Image, ImageTk
from ttkbootstrap.constants import *

from src.gui.toast import create_toast


async def generate_qrcode(
    text: str, output_label: ttk.Label, fill_color="black", back_color="white"
):
    """
    Generate a QR code from the given text and display it in the provided label.

    Args:
        text (str): The text to encode in the QR code.
        output_label (ttk.Label): The label where the QR code will be displayed.
        fill_color (str): The color of the QR code. Default is "black".
        back_color (str): The background color of the QR code. Default is "white".

    Returns:
        bool: True if the QR code was generated successfully, False otherwise.
    """
    try:
        # Create a QR code object with specified settings
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)  # Add data to the QR code
        qr.make(fit=True)

        # Convert the QR code to a PIL image
        qr_img = qr.make_image(fill_color=fill_color, back_color="orange")
        qr_img = qr_img.resize((500, 500), resample=Image.Resampling.LANCZOS)

        # Convert the PIL image to a format compatible with Tkinter
        photo = ImageTk.PhotoImage(qr_img)

        # Display the QR code in the provided label
        output_label.config(image=photo)
        output_label.image = photo  # Keep a reference to prevent garbage collection
        return True
    except Exception as e:
        # Display an error message if QR code generation fails
        create_toast("Error", f"Failed to generate QR code: {e}")
        return False
