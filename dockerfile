# Use the official lightweight Python image as the base
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /toybank

# Copy files and directories
COPY requirements.txt .
COPY app/ app/

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that Flask will run on inside the container
EXPOSE 8000

# Set the environment variable for Flask to know where the app is
ENV FLASK_APP=app/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8000

# Command to run the application using the Flask development server
CMD ["flask", "run"]