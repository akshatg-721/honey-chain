import base64
import io
import os

import qrcode


def generate_qr_code(batch_id: str) -> str:
    """
    Generate a QR code encoding the consumer verification URL for a batch.

    Returns a base64-encoded PNG as an HTML data URI:
        data:image/png;base64,<encoded>

    The QR image can be embedded directly in an <img src="..."> tag
    or stored as-is in the database — no file system or S3 required.
    """
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    verify_url = f"{frontend_url}/verify/{batch_id}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(verify_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    encoded_str = base64.b64encode(buffer.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded_str}"
