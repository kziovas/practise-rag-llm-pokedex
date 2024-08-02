# Use Python 3.11.8 base image
FROM python:3.11.8-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies including NLTK
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK Punkt tokenizer
RUN python -c "import nltk; nltk.download('punkt')"

# Copy the rest of the application code to the working directory
COPY . .

# Expose the port that the app runs on
EXPOSE 8000

# Command to run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
