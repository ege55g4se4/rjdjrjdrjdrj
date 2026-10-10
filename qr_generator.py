# qr_generator.py - Local QR Code Generator for MX-UI (No Text)
import qrcode
from PIL import Image
import io
import base64
from typing import Optional

def generate_qr_base64(data: str, size: int = 300) -> str:
    """
    Generate QR code as Base64 string for HTML embedding (no text)
    
    Args:
        data: Data to encode in QR code
        size: Desired image size in pixels
    
    Returns:
        str: Base64 encoded PNG image
    """
    # Calculate box size based on desired image size
    box_size = max(4, size // 30)
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # Generate image - clean QR without text
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to Base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_base64}"

def generate_qr_file(data: str, filename: str = "qr.png", size: int = 20) -> str:
    """
    Generate QR code and save to file (no text)
    
    Args:
        data: Data to encode
        filename: Output filename
        size: QR box size
    
    Returns:
        str: Path to saved file
    """
    qr = qrcode.QRCode(version=1, box_size=size, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    return filename

# Simple function for quick usage
def qr(data, filename="qr.png", size=20):
    """Quick QR generation function (no text)"""
    return generate_qr_file(data, filename, size)