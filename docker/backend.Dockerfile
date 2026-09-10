COPY backend ./backend
COPY ml ./ml
COPY models ./models

RUN python -c "import urllib.request; urllib.request.urlretrieve('https://github.com/debashis-sharingan-21/steelvision/releases/download/v1.0.0/best.pt', 'models/best.pt')"