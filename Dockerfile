FROM ubuntu:latest

# Add amd64 architecture and install necessary dependencies
RUN dpkg --add-architecture amd64 && \
    apt-get update && apt-get install -y \
    libstdc++6 \
    libtiff-dev libgeotiff-dev libgdal-dev \
    libboost-system-dev libboost-thread-dev libboost-filesystem-dev libboost-program-options-dev libboost-regex-dev libboost-iostreams-dev libtbb-dev \
    git cmake build-essential wget \
    libc6 \
    binutils:amd64 \
    s3cmd \
    && rm -rf /var/lib/apt/lists/*

# Create a directory for your binary
WORKDIR /app

# Copy the shared library and binary
COPY liblaszip.so /app/
COPY PotreeConverter /app/

# Make your binary executable
RUN chmod +x /app/PotreeConverter

# Use LD_PRELOAD to directly link the library when running the binary
# Keep --help as default but allow passing arguments from docker run command
# ENTRYPOINT [ "sh", "-c", "LD_PRELOAD=/app/liblaszip.so /app/PotreeConverter $*", "--" ]
# CMD ["--help"]


# Copy our custom entrypoint script that runs conversion then S3 upload
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Use the custom entrypoint
ENTRYPOINT ["/entrypoint.sh"]
CMD ["--help"]
