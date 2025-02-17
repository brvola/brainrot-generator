FROM python:3.10-slim

WORKDIR /app

# Install system dependencies required for moviepy and other packages
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    build-essential \
    python3-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# Configure ImageMagick policy to be less restrictive
RUN mv /etc/ImageMagick-6/policy.xml /etc/ImageMagick-6/policy.xml.bak && \
    echo '<?xml version="1.0" encoding="UTF-8"?>\n\
<policymap>\n\
  <policy domain="resource" name="memory" value="2GiB"/>\n\
  <policy domain="resource" name="map" value="4GiB"/>\n\
  <policy domain="resource" name="width" value="16KP"/>\n\
  <policy domain="resource" name="height" value="16KP"/>\n\
  <policy domain="resource" name="area" value="1GB"/>\n\
  <policy domain="resource" name="disk" value="8GiB"/>\n\
  <policy domain="coder" rights="read|write" pattern="*" />\n\
  <policy domain="system" rights="read|write" pattern="*" />\n\
  <policy domain="path" rights="read|write" pattern="@*" />\n\
  <policy domain="path" rights="read|write" pattern="*" />\n\
</policymap>' > /etc/ImageMagick-6/policy.xml

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directories for content and videos
RUN mkdir -p content videos fonts

# Verify ImageMagick installation and configuration
RUN convert -list policy 