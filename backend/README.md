# Media Downloader (Backend)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-2023.11.16-orange)](https://github.com/yt-dlp/yt-dlp)
[![Docker](https://img.shields.io/badge/Docker-✓-2496ED)](https://www.docker.com/)

A high-performance backend service for downloading YouTube media.

---

## 🌟 Features

- **YouTube & Beyond**: Download videos/audio from YouTube (other platforms - coming soon).
- **Dockerized**: Pre-configured for seamless deployment.
- **Advanced Formatting**: Choose video/audio quality and merge streams with FFmpeg.

---

## 📂 Directory Structure

```
backend/
├── app/
│   ├── core/                     # Core application components
│   │   ├── config_settings.py    # Application configuration management
│   │   └── exceptions.py         # Custom exception definitions
│   │
│   ├── models/                   # Database models
│   │   └── youtube.py            # YouTube-related data models (Empty right now)
│   │
│   ├── routers/                  # API route definitions
│   │   └── youtube_router.py     # YouTube-related endpoints
│   │
│   ├── schemas/                  # Pydantic schemas
│   │   └── youtube_schema.py     # Data validation schemas for YouTube
│   │
│   ├── services/                 # Business logic implementation
│   │   ├── aws_service.py        # AWS integration service
│   │   └── youtube_service.py    # YouTube business logic
│   │
│   ├── utils/                    # Utility functions
│   │   └── validator.py          # Input validation utilities
│   │
│   └── main.py                   # Application entry point
│
├── .env                          # Environment variables
├── Dockerfile                    # Container configuration
├── docker-compose.yml            # Container orchestration
├── requirements.txt              # Python dependencies
└── README.md                     # Project documentation
```

---

## Environment Variables

The application uses environment variables for configuration. Create a .env file in the root directory with the
following variables:

```
# CORS Config
ALLOWED_ORIGINS='["*"]'
ALLOW_CREDENTIALS=True
ALLOW_METHODS='["*"]'
ALLOW_HEADERS='["*"]'

# Server Configuration
APP_DEBUG=True / False

# AWS Credentials
AWS_ACCESS_KEY_ID_VALUE=your_access_key
AWS_SECRET_ACCESS_KEY_VALUE=your_secret_key
AWS_REGION=your_region
S3_BUCKET_NAME=your_bucket_name
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- FFmpeg (for merging audio/video)
- Docker (optional)

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/SunnyYadav16/Media-Downloader.git
   cd Media-Downloader/backend

2. **Install Dependencies**:
   ```bash
    pip install -r requirements.txt
    ```

3. **Install FFmpeg**:
   ```bash
   - Download from https://github.com/yt-dlp/FFmpeg-Builds
   - Add to your system PATH
   - Verify installation: ffmpeg -version  
   ```

4. **Run the Service (using Docker)**:
    ```bash
    docker compose build
    docker compose up
    ```

5. **Run the Service Locally**:
    ```bash
   uvicorn app.main:app --reload
   ``` 
   OR
   ```bash
   fastapi dev app/main.py
   ```
   
---

## FFmpeg Requirement
- FFmpeg is a required dependency for video and audio processing operations. Before running the application:

   1. Install FFmpeg and ensure it's accessible in your system's PATH
   2. You can obtain FFmpeg builds from: https://github.com/yt-dlp/FFmpeg-Builds
   3. Verify your installation by running ffmpeg -version in your terminal

### Available Builds
The repository provides static builds for multiple platforms:

**Linux**:
- x64 (64-bit)
- ARM64 (aarch64)

**Windows**:
- x86 (32-bit)
- x64 (64-bit)
- ARM64


### Important Note
1. There are currently no **MacOS** builds
2. These builds are specifically optimized for use with yt-dlp.

---

## 🤝 Contributing

1. Fork the repository.
2. Create a branch: git checkout -b feature/your-feature.
3. Commit changes: git commit -m "Add your feature".
4. Push to the branch: git push origin feature/your-feature.
5. Open a pull request.