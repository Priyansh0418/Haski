FROM python:3.11-slim

# Prevents Python from writing .pyc files and buffers stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies needed for many Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	gcc \
	libffi-dev \
	libssl-dev \
	&& rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY ./app /app/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
