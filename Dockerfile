# Dockerfile for FastAPI app
# Use a production-ready Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source code
COPY ./ /app

# Expose port
EXPOSE 8000

# Start the FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
