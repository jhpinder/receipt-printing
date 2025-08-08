from flask import Flask, render_template_string, request, redirect, url_for, flash
from escpos.printer import Network
from PIL import Image
import os
import tempfile

app = Flask(__name__)
import secrets
app.secret_key = secrets.token_urlsafe(32)  # Secure random secret key for flash messages
# Allow overriding printer IP via environment variable PRINTER_IP (defaults to previous hard-coded value)
printer_ip = os.getenv("PRINTER_IP", "192.168.50.210")

from flask import render_template

@app.route('/', methods=['GET', 'POST'])
def print_task():
    if request.method == 'POST':
        task_name = request.form.get('task_name')
        due_date = request.form.get('due_date')
        image_file = request.files.get('image')

        # Connect to printer
        try:
            printer = Network(printer_ip)
        except Exception as e:
            flash(f"Printer connection failed: {e}")
            return redirect(url_for('print_task'))

        # Print text
        try:
            printer.text(f"Task: {task_name}\nDue: {due_date}\n\n")
        except Exception as e:
            flash(f"Failed to print text: {e}")
            return redirect(url_for('print_task'))

        # Print image if provided
        if image_file and image_file.filename:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_img:
                    img = Image.open(image_file)
                    printable_width = 512
                    w_percent = (printable_width / float(img.size[0]))
                    h_size = int((float(img.size[1]) * float(w_percent)))
                    img = img.resize((printable_width, h_size), Image.LANCZOS)
                    img.save(temp_img.name)
                    printer.image(temp_img.name)
                os.remove(temp_img.name)
            except Exception as e:
                flash(f"Failed to print image: {e}")
                return redirect(url_for('print_task'))

        try:
            printer.cut()
        except Exception:
            pass  # Some printers may not support cut

        flash("Printed successfully!")
        return redirect(url_for('print_task'))

    return render_template('print_form.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
