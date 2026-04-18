# Start from a lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
# All subsequent commands run from here
WORKDIR /app

# Copy requirements first — Docker caches this layer
# so it won't reinstall packages every time you change app code
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code
COPY . .

# Start the FastAPI server
# host=0.0.0.0 makes it accessible outside the container
# port=8000 is the standard FastAPI port
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]