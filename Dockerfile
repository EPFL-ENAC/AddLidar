FROM alpine:latest

# Install runtime dependencies only
RUN apk add --no-cache \
    libstdc++ \
    libtiff \
    tbb-dev \
    boost-system \
    boost-thread \
    boost-filesystem \
    boost-program_options \
    boost-regex \
    boost-iostreams \
    py3-s3cmd

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