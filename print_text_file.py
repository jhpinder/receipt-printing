from escpos.printer import Network
import sys

printer_ip = "192.168.50.210"
text_file = "printme.txt"

def main():
    try:
        printer = Network(printer_ip)
    except Exception as e:
        print(f"Failed to connect to printer at {printer_ip}: {e}")
        sys.exit(1)

    try:
        with open(text_file, 'r', encoding='utf-8') as f:
            content = f.read()
        printer.text(content)
        printer.cut()
        print(f"Contents of {text_file} sent to printer at {printer_ip}")
    except Exception as e:
        print(f"Failed to print text: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
