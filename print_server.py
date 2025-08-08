from flask import Flask, render_template_string, request, redirect, url_for, flash
from escpos.printer import Network
from PIL import Image
import os
import tempfile

app = Flask(__name__)
import secrets
app.secret_key = secrets.token_urlsafe(32)  # Secure random secret key for flash messages
printer_ip = "192.168.50.210"

HTML_FORM = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Print Task</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <h2>Print Task</h2>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <div class="flash">{{ messages[0] }}</div>
          {% endif %}
        {% endwith %}
        <form method="post" enctype="multipart/form-data">
            <label for="task_name">Task Name:</label>
            <input type="text" id="task_name" name="task_name" required>

            <label for="due_date">Due Date:</label>
            <input type="date" id="due_date" name="due_date" required>

            <label for="image">Image (optional):</label>
            <input type="file" id="image" name="image" accept="image/*">

            <button type="submit">Print</button>
        </form>
    </div>
</body>
</html>
'''

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

    return render_template_string(HTML_FORM)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
