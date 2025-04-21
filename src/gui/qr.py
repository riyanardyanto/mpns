import qrcode
import ttkbootstrap as ttk
from PIL import Image, ImageTk
from ttkbootstrap.constants import *

from src.gui.toast import create_toast


async def generate_qrcode(text: str, output_label: ttk.Label):
    try:
        # Membuat QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        # Mengonversi QR code ke gambar PIL
        qr_img = qr.make_image(fill_color="black", back_color="orange")
        qr_img = qr_img.resize((500, 500), resample=Image.LANCZOS)

        # Mengonversi ke format yang kompatibel dengan tkinter
        photo = ImageTk.PhotoImage(qr_img)
        # return photo

        # Menampilkan gambar di label
        output_label.config(image=photo)
        output_label.image = photo  # Simpan referensi untuk mencegah garbage collection
        return True
    except Exception as e:
        create_toast("Error", f"Failed to generate QR code: {e}")
        return False
