from PIL import Image

def convert_png_to_ico(png_path, ico_path, sizes=None):
    """
    Convert PNG to ICO format
    :param png_path: Path to input PNG file
    :param ico_path: Path to output ICO file
    :param sizes: List of sizes for the ICO file (default: [16, 32, 48, 64, 128, 256])
    """
    if sizes is None:
        sizes = [16, 32, 48, 64, 128, 256]  # Common icon sizes
    
    # Open the PNG image
    img = Image.open(png_path)
    
    # Convert to ICO format with multiple sizes
    img.save(ico_path, format='ICO', sizes=[(size, size) for size in sizes])

# Example usage
convert_png_to_ico('assets/icon.png', 'assets/icon.ico') 