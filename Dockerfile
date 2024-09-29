# Use an official Python runtime as a parent image
FROM python:3.13.0rc2-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port available to the world outside this container
# (Modify this if your application uses a specific port)
EXPOSE 8000

# Define environment variable
# (Set environment variables used by your application)
ENV NAME pycgapi

# Run the application when the container launches
# (Modify the command based on how you run your application, e.g., python script or a web server)
CMD ["python", "examples/example.py"]
