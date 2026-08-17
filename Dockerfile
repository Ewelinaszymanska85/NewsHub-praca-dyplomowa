FROM python:3.14-slim
WORKDIR /app

# Biblioteki systemowe wymagane do skompilowania Pillow (obsługa obrazów)
RUN apt-get update && apt-get install -y --no-install-recommends \
    zlib1g-dev \
    libjpeg-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 