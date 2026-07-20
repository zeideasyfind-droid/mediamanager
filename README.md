# EasyFind Property Formatter

Complete web application for property listing automation with AI-powered image enhancement and WhatsApp message formatting.

## Overview

This application allows operators to:
- Upload raw property details and images
- Automatically enhance images using Vertex AI
- Normalize property details using EasyFind formatting rules
- Generate ready-to-share WhatsApp messages
- Create organized Google Drive folders with enhanced images

## Architecture

- **Frontend**: Next.js (React + TypeScript)
- **Backend**: FastAPI (Python 3.11)
- **Background Processing**: Cloud Run + Pub/Sub
- **Storage**: Google Cloud Storage + Google Drive
- **AI**: Vertex AI (Gemini 2.5 Pro for text, Image Enhancement for photos)

## Quick Start

```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install

# Run locally
npm run dev
```

## Documentation

See `/docs` for detailed implementation guides:
- [Implementation Guide](docs/IMPLEMENTATION_GUIDE.md)
- [API Specification](docs/API_SPEC.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Configuration](docs/CONFIGURATION.md)

## Repository Structure

```
├── frontend/          # Next.js application
├── backend/           # FastAPI application
├── subscriber/        # Pub/Sub background processor
├── infrastructure/    # Terraform + Docker configs
├── docs/             # Documentation
├── tests/            # Test suite
├── config/           # Environment configs
└── scripts/          # Deployment scripts
```

## License

Private - EasyFind
