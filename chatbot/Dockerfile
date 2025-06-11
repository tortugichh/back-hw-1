# Use a Python base image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app/chatbot

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the chatbot application code
COPY . /app/chatbot/

# Command to run the chatbot
CMD ["python", "-m", "chatbot.main"] 