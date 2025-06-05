FROM python:3.9-alpine

# Set the working directory
WORKDIR /app

# Copy the necessary files into the container
COPY scanner.py .
COPY job-batch-lidar-zip.template.yaml .
COPY job-batch-potree-converter.template.yaml .
COPY persist_state.sql .

# Install required dependencies
RUN apk add --no-cache \
    py3-pip \
    bash \
    && pip install --no-cache-dir \
    kubernetes \
    pydantic \
    jinja2 \
    sqlite-utils

# Command to run the script with the specified arguments
CMD ["python", "scanner.py", "--original-root", "/lidar", "--zip-root", "/zips", "--db-path", "/db-path/archive.db"]