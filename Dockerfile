FROM python:3.9-slim

# Create and set the base working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files into the container
COPY . .

# Change the working directory to the 'app' folder
WORKDIR /app/app

# Run the application
CMD ["python", "app.py"]
