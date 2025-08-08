# Receipt Printing Service

Flask web interface + scripts to send tasks and images to an ESC/POS network printer.

## Features
- Print task name + due date + optional image via web form.
- Print arbitrary image from CLI (`print_image.py`).
- Print text file (`print_text_file.py`).
- Dark mode responsive UI.
- Containerized deployment.

## Environment Variables
- `PRINTER_IP` (default `192.168.50.210`): Network printer IP.

## Local Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python print_server.py
```
Open http://localhost:5050

## Docker Build & Run
```bash
# Build image
docker build -t receipt-printing:latest .

# Run (override printer IP if needed)
docker run --rm -e PRINTER_IP=192.168.50.210 -p 5050:5050 receipt-printing:latest
```

## Updating Printer IP Permanently
Edit `PRINTER_IP` env in Docker run command or set in an `.env` (compose).

## Docker Compose (optional)
Example `docker-compose.yml`:
```yaml
services:
  receipt:
    build: .
    ports:
      - "5050:5050"
    environment:
      PRINTER_IP: 192.168.50.210
```
Run:
```bash
docker compose up --build
```

## Notes
- Ensure the container can reach the printer IP on the network (bridge vs host networking).
- If printing fails, check network routing and that the printer listens on port 9100.
