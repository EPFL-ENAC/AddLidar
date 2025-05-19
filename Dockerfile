# Base stage with Ubuntu for libraries
FROM ubuntu:22.04 AS base

# Install required libraries to have the files available
RUN apt-get update && apt-get install -y \
    libstdc++6 \
    libtiff5 \
    libboost-system1.74.0 \
    libboost-thread1.74.0 \
    libboost-filesystem1.74.0 \
    libboost-program-options1.74.0 \
    libboost-regex1.74.0 \
    libboost-iostreams1.74.0

# Runtime stage with Debian slim
FROM debian:bullseye-slim

# Create necessary directories
RUN mkdir -p /lib/x86_64-linux-gnu /usr/lib/x86_64-linux-gnu

# Copy core libraries from Ubuntu
COPY --from=base /lib/x86_64-linux-gnu/libc.so.6* /lib/x86_64-linux-gnu/
COPY --from=base /lib/x86_64-linux-gnu/libm.so.6* /lib/x86_64-linux-gnu/
COPY --from=base /lib/x86_64-linux-gnu/libpthread.so.0* /lib/x86_64-linux-gnu/
COPY --from=base /lib/x86_64-linux-gnu/libdl.so.2* /lib/x86_64-linux-gnu/
COPY --from=base /lib/x86_64-linux-gnu/librt.so.1* /lib/x86_64-linux-gnu/
COPY --from=base /lib64/ld-linux-x86-64.so.2* /lib64/

# Copy C++ standard libraries
COPY --from=base /usr/lib/x86_64-linux-gnu/libstdc++.so.6* /usr/lib/x86_64-linux-gnu/
COPY --from=base /usr/lib/x86_64-linux-gnu/libgcc_s.so.1* /usr/lib/x86_64-linux-gnu/

# Copy tiff libraries
COPY --from=base /usr/lib/x86_64-linux-gnu/libtiff.so* /usr/lib/x86_64-linux-gnu/

# Copy boost libraries
COPY --from=base /usr/lib/x86_64-linux-gnu/libboost_system.so* /usr/lib/x86_64-linux-gnu/
COPY --from=base /usr/lib/x86_64-linux-gnu/libboost_thread.so* /usr/lib/x86_64-linux-gnu/
COPY --from=base /usr/lib/x86_64-linux-gnu/libboost_filesystem.so* /usr/lib/x86_64-linux-gnu/
COPY --from=base /usr/lib/x86_64-linux-gnu/libboost_program_options.so* /usr/lib/x86_64-linux-gnu/
COPY --from=base /usr/lib/x86_64-linux-gnu/libboost_regex.so* /usr/lib/x86_64-linux-gnu/
COPY --from=base /usr/lib/x86_64-linux-gnu/libboost_iostreams.so* /usr/lib/x86_64-linux-gnu/


# Create app directory
WORKDIR /app

# Copy application files
COPY PotreeConverter/liblaszip.so /app/
COPY PotreeConverter /app/
COPY entrypoint.sh /entrypoint.sh

# Set permissions
RUN chmod +x /app/PotreeConverter /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["--help"]