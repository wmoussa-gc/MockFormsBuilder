# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN python -c "import tomllib; f=open('pyproject.toml','rb'); data=tomllib.load(f); f.close(); open('requirements.txt', 'w').write('\n'.join(data['project']['dependencies']))"
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8081

# Start the API using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8081", "main:app"]