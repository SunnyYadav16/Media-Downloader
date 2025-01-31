# Use the latest Ubuntu image with Alpine compatibility
FROM ubuntu:22.04

# Set the working directory inside the container
WORKDIR /backend

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    tar \
    && rm -rf /var/lib/apt/lists/*

# Download and install the FFmpeg build
RUN wget -q https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linuxarm64-gpl.tar.xz \
    && tar -xf ffmpeg-master-latest-linuxarm64-gpl.tar.xz \
    && mv ffmpeg-master-latest-linuxarm64-gpl /usr/local/ffmpeg \
    && rm ffmpeg-master-latest-linuxarm64-gpl.tar.xz

# Add FFmpeg to the PATH
ENV PATH="/usr/local/ffmpeg/bin:$PATH"

# Copy FastAPI application files into the container
COPY . /backend

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
