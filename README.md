# AgriFinance Mobile Platform

A cutting-edge mobile-first platform designed to empower African farmers with AI-driven financial services and climate-smart agricultural insights.

## Overview

AgriFinance combines AI, satellite imagery, and financial technology to create a revolutionary solution for agricultural financing in regions like Ghana and Kenya. The platform provides farmers with day-to-day utility while enabling financial institutions to make data-driven lending decisions through innovative credit scoring.

## Key Innovations

- **AI-Powered Credit Scoring**: Machine learning models that adapt to each farmer's unique context, improving loan approval rates
- **Progressive Web App (PWA)**: Offline-first design ensuring functionality in areas with intermittent connectivity
- **Voice & Visual Interfaces**: Multilingual voice input/output supporting low-literacy users
- **Satellite-Driven Crop Monitoring**: AI analysis of NDVI data presented as simple visual health indicators
- **Climate-Adjusted Loans**: Dynamic loan terms that adapt to weather events and climate conditions
- **Farmer-Centric Design**: Intuitive interfaces with cultural relevance and high-contrast elements for outdoor visibility

## Technical Stack

- **Backend**: Flask API with SQLAlchemy
- **Mobile Frontend**: Progressive Web App with offline capabilities
- **AI/ML**: TensorFlow Lite for on-device inference
- **Data Storage**: SQLite with sync capabilities for offline-to-online transitions
- **APIs**: Integration with weather services, satellite imagery, and voice recognition

## Getting Started

### Running the API Server

```bash
# Clone the repository
git clone https://github.com/Jonathan-321/supreme-spork.git
cd supreme-spork

# Install dependencies
pip install -r requirements.txt

# Run the API server
python api_server.py
```

The API server will be available at http://localhost:8000

### API Documentation

Core endpoints:
- `/api/farmers` - Farmer registration and management
- `/api/farms` - Farm registration and monitoring
- `/api/loans` - Loan applications and management
- `/api/weather` - Weather forecasts and climate risk assessment
- `/api/credit` - AI-driven credit scoring

## Project Structure

- `/api`: API backend with RESTful endpoints
  - `/models`: Database models for farmers, farms, loans, and climate data
  - `/routes`: API route definitions
  - `/services`: Business logic and AI services
- `/mobile`: Mobile PWA frontend (coming soon)
- `/ml`: Machine learning models for credit scoring and crop analysis (coming soon)

## Future Roadmap

- **Blockchain Integration**: Transparent loan transactions and supply chain tracking
- **IoT Connectivity**: Integration with soil moisture sensors and weather stations
- **Expanded Voice Interface**: Complete voice-driven application navigation
- **AR Visualization**: Augmented reality for visualizing crop health directly on farms

## YC Summer Grant Program

This project is being developed for the YC Summer Grant Program, focusing on innovative technology solutions for agricultural financing in Africa.