import argparse
from escpos.printer import Network
from PIL import Image
import sys

# Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Send image to ESC/POS network printer.")
    parser.add_argument('--image', required=True, help='Path to the image file to print')
    return parser.parse_args()

def main():
    args = parse_args()
    image_path = args.image

    # Connect to the printer
    printer_ip = "192.168.50.210"
    try:
        printer = Network(printer_ip)
    except Exception as e:
        print(f"Failed to connect to printer at {printer_ip}: {e}")
        sys.exit(1)

    # Open, scale, and print the image
    try:
        img = Image.open(image_path)
        # ESC/POS printers typically have a printable width of 512 pixels (adjust as needed)
        printable_width = 512
        w_percent = (printable_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((printable_width, h_size), Image.LANCZOS)
        # Save to a temporary file
        temp_path = "_temp_scaled_image.png"
        img.save(temp_path)
        printer.image(temp_path)
        printer.cut()
        print(f"Image sent to printer at {printer_ip}")
        # Delete the temporary image file
        import os
        try:
            os.remove(temp_path)
        except Exception as remove_err:
            print(f"Warning: could not delete temp image: {remove_err}")
    except Exception as e:
        print(f"Failed to print image: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
