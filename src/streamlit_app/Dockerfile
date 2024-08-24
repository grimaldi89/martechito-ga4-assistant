# Define the base image
FROM python:3.10.12

# Define the working directory in the container
WORKDIR /app


# Copy the project files to the working directory in the container
COPY . .
# Install the Python dependencies listed in the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that the application will run on
EXPOSE 8501

# Give execution permission to the script
RUN chmod +x /app/start.sh

# Define the shell script as the entry point of the container
ENTRYPOINT ["/app/start.sh"]

# You need to define the environment variables QDRANT_URL, QDRANT_API_KEY and OPENAI_API_KEY.
# After that, you can build the image and run the  container with the following commands:
