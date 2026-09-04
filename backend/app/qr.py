import io
import os
import qrcode

FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")


def get_verification_url(batch_id: str) -> str:
    """Generate the consumer-facing verification web URL for a given batch."""
    return f"{FRONTEND_BASE_URL}/verify/{batch_id}"


def generate_qr_image(batch_id: str) -> bytes:
    """
    Generate an in-memory PNG QR code image encoding the verification URL.
    Returns raw PNG bytes on demand without writing to the filesystem.
    """
    url = get_verification_url(batch_id)
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def generate_qr_code_url(batch_id: str) -> str:
    """Helper returning the verification URL for storing in Batch.qr_code_url."""
    return get_verification_url(batch_id)
