# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip --default-timeout=100 --retries 5 --index-url https://pypi.org/simple && \
    pip install --no-cache-dir -r requirements.txt --default-timeout=100 --retries 5 --index-url https://pypi.org/simple

# Copy the rest of the application code
COPY . .

# Create a .env file from the example
# RUN cp .env.example .env

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]