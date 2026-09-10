# Pinned to 3.11 for mature wheel availability across the
# torch/ultralytics/opencv stack.
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY ml ./ml
COPY models ./models

RUN python -c "import urllib.request; urllib.request.urlretrieve('https://github.com/debashis-sharingan-21/steelvision/releases/download/v1.0.0/best.pt', 'models/best.pt')"

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]