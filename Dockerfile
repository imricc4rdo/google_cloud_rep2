# Use the official lightweight Python image.
FROM python:3.10.14

# Install Git and Git LFS
RUN apt-get update && apt-get install -y git git-lfs && git lfs install

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

# Set the working directory
ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy the local code to the container image
COPY . ./

# Pull LFS files
RUN git lfs pull

# Install Python dependencies
RUN pip install -r requirements.txt
RUN pip install gunicorn

# Run the web service on container startup
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app