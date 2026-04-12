FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

WORKDIR /app

# Copy requirements
COPY requirements.txt /app/

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the app source code
COPY . /app/

# Expose the Flask port
EXPOSE 5000

# Start Gunicorn server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]