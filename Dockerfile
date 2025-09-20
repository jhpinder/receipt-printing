# Use slim Python base image
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

# System dependencies for Pillow (JPEG, zlib) and escpos (may need libusb)
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  libjpeg-dev \
  zlib1g-dev \
  libusb-1.0-0 \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Set timezone to US new york
ENV TZ=America/New_York
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy application code
COPY . .

# Expose Flask port
EXPOSE 5050

# Environment variable hint (override at run time)
ENV PRINTER_IP=192.168.50.210 \
  FLASK_APP=print_server.py \
  FLASK_RUN_HOST=0.0.0.0 \
  FLASK_RUN_PORT=5050

# Default command
CMD ["python", "print_server.py"]
