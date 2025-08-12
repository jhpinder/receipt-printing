import argparse
import time
import os
import sys
import tempfile
from escpos.printer import Network
from PIL import Image


def parse_args():
    parser = argparse.ArgumentParser(description="Print a text file and then an image underneath to an ESC/POS network printer.")
    parser.add_argument("--text", required=True, help="Path to the text file to print")
    parser.add_argument("--image", required=True, help="Path to the image file to print underneath")
    return parser.parse_args()


def prepare_image_segments(image_path: str, width: int = 512, max_height: int = 72):
    """Open image, auto-orient using EXIF, scale to width, and yield path(s) to segments under max_height.

    max_height is in pixels per printer command block; adjust to your device if needed.
    """
    img = Image.open(image_path)
    # Auto-orient JPEGs based on EXIF like in the server
    try:
        exif = getattr(img, "_getexif", lambda: None)()
        if exif:
            orientation = exif.get(274)
            if orientation == 3:
                img = img.rotate(180, expand=True)
            elif orientation == 6:
                img = img.rotate(270, expand=True)
            elif orientation == 8:
                img = img.rotate(90, expand=True)
    except Exception:
        pass

    # Scale to target width, maintain aspect ratio
    w_percent = width / float(img.size[0])
    h_size = int(float(img.size[1]) * w_percent)
    img = img.resize((width, h_size), Image.LANCZOS)

    # Split into segments and yield temp file paths
    if img.height <= max_height:
        # If image is shorter than max_height, print as one segment
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp_path = tmp.name
        tmp.close()
        img.save(tmp_path)
        yield tmp_path
    else:
        num_segments = (img.height + max_height - 1) // max_height
        for i in range(num_segments):
            upper = i * max_height
            lower = min((i + 1) * max_height, img.height)
            segment = img.crop((0, upper, width, lower))
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            tmp_path = tmp.name
            tmp.close()
            segment.save(tmp_path)
            yield tmp_path


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
    
    # Connect to printer
    try:
        printer_ip = os.getenv("PRINTER_IP", "192.168.50.210")
        printer = Network(printer_ip)
    except Exception as e:
        print(f"Failed to connect to printer: {e}")
        sys.exit(1)

    # Print text
    try:
        with open(args.text, "r", encoding="utf-8") as f:
            content = f.read()
        printer.text(content)
        printer.text("\n")
    except Exception as e:
        print(f"Failed to print text: {e}")
        sys.exit(1)

    print_image(image_path, printer)
    print(f"Image sent to printer at {printer_ip}")


def print_image(image_path, printer):

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

        printer.ln()
        printer.cut()

    except Exception as e:
        print(f"Failed to print image: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
