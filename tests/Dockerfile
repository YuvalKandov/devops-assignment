FROM python:3.11-slim

WORKDIR /app

# Copy test script (uses stdlib only - no pip install needed)
COPY test_nginx.py .

# Ensure output is not buffered
ENV PYTHONUNBUFFERED=1

# Run tests
ENTRYPOINT ["python", "test_nginx.py"]
