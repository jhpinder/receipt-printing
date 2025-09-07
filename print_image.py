import argparse
import time
from escpos.printer import Network
from PIL import Image
import sys
import os

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
        printable_width = 512
        max_height = 72  # ESC/POS typical max height per image command

        # Resize image to printable width, keep aspect ratio
        w_percent = printable_width / float(img.size[0])
        h_size = int(float(img.size[1]) * w_percent)
        img = img.resize((printable_width, h_size), Image.LANCZOS)

        # Segment and print
        num_segments = (img.height + max_height - 1) // max_height
        for i in range(num_segments):
            upper = i * max_height
            lower = min((i + 1) * max_height, img.height)
            segment = img.crop((0, upper, printable_width, lower))
            temp_path = f"_temp_segment_{i}.png"
            segment.save(temp_path)
            printer.image(temp_path)
            try:
                os.remove(temp_path)
            except Exception as remove_err:
                print(f"Warning: could not delete temp image: {remove_err}")

        time.sleep(0.5)
        printer.cut()
        print(f"Image sent to printer at {printer_ip}")

    except Exception as e:
        print(f"Failed to print image: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
