FROM python:3.11-slim

# Prevent Python from writing bytecode
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies & Node.js
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Build frontend and collect static files
RUN cd frontend && npm install && npm run build && cd ..
RUN python manage.py collectstatic --no-input

EXPOSE 8000

CMD ["gunicorn", "smart_farming.wsgi:application", "--bind", "0.0.0.0:8000"]
