FROM alpine:latest

# Add community repository and install runtime dependencies
RUN apk add --no-cache --update \
    libstdc++ \
    tiff-dev \
    boost-system \
    boost-thread \
    boost-filesystem \
    boost-program_options \
    boost-regex \
    boost-iostreams \
    python3 \
    py3-pip

# Install s3cmd via pip since py3-s3cmd isn't available
RUN pip3 install --no-cache-dir --break-system-packages s3cmd

# Create app directory
WORKDIR /app

# Copy only the required files
COPY liblaszip.so /app/
COPY PotreeConverter /app/
COPY entrypoint.sh /entrypoint.sh

# Set permissions
RUN chmod +x /app/PotreeConverter /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["--help"]