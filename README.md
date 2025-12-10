# Weather Data Collection System

A DevOps weather data collection system demonstrating:
- **External API Integration** (OpenWeather API)
- **Cloud Storage** (AWS S3)
- **Infrastructure as Code**
- **Version Control** (Git)
- **Python Development**
- **Error Handling**
- **Environment Management**

## Features

- Fetches real-time weather data for multiple cities
- Displays temperature (°F), humidity, and weather conditions
- Automatically stores weather data in AWS S3
- Supports multiple cities tracking
- Timestamps all data for historical tracking

## Technical Architecture

**Technology Stack:**
- Python 3.x
- AWS S3
- OpenWeather API
- boto3 (AWS SDK)
- python-dotenv
- requests

### System Architecture Diagram

![Weather Data Collection System Architecture](architecture_diagram.png)

The diagram above shows the complete system architecture including:
- **Environment Configuration** - Secure credential management with .env files
- **Python Application** - Main weather collector with API integration
- **Infrastructure as Code** - Automated AWS S3 setup and configuration
- **External API** - OpenWeather API for real-time weather data
- **AWS Cloud** - S3 bucket for data storage with versioning
- **Local Backup** - Redundant local storage
- **Data Flow** - Clear arrows showing how data moves through the system
- **DevOps Principles** - Automation, IaC, version control, security

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.7+** installed
2. **OpenWeather API Key** - [Get it here](https://openweathermap.org/api)
3. **AWS Account** with:
   - AWS Access Key ID
   - AWS Secret Access Key
   - S3 bucket created
4. **Git** installed

## Installation & Setup

### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd weather-data-collection
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` file with your credentials:
   ```env
   OPENWEATHER_API_KEY=your_actual_api_key
   AWS_ACCESS_KEY_ID=your_aws_access_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=your-bucket-name
   ```

### Step 5: Set Up AWS S3 Bucket

1. Log in to AWS Console
2. Navigate to S3 service
3. Create a new bucket (or use existing one)
4. Note the bucket name and region
5. Ensure your IAM user has S3 write permissions

**Required IAM Permissions:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:PutObjectAcl"
            ],
            "Resource": "arn:aws:s3:::your-bucket-name/*"
        }
    ]
}
```

## Usage

Run the weather data collector:

```bash
python weather_collector.py
```

### Sample Output

```
============================================================
Weather Data Collection System - Starting
============================================================

Processing: New York
✓ Successfully fetched weather data for New York
## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   copy .env.example .env
   # Edit .env with your API keys
   ```

3. **Set up AWS S3 (Infrastructure as Code):**
   ```bash
   python infrastructure_setup.py
   ```

4. **Run the application:**
   ```bash
   python weather_collector.py
   ```

5. **Verify (optional):**
## Project Structure

```
weather-data-collection/
├── weather_collector.py              # Main application
├── infrastructure_setup.py           # Infrastructure as Code (AWS S3 setup)
├── verify_setup.py                   # Verification script
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment template
├── .gitignore                        # Git ignore
├── README.md                         # Documentation
└── architecture_diagram.png          # System architecture diagram
``` "humidity": 65,
    "pressure": 1013,
    "weather_condition": "Clouds",
    "weather_description": "partly cloudy",
    "wind_speed_mph": 8.5,
    "country": "US",
    "latitude": 40.7128,
    "longitude": -74.0060
  }
]
```

## Error Handling

The system includes comprehensive error handling for:

- ✅ Missing environment variables
- ✅ API request failures
- ✅ AWS S3 upload errors
- ✅ Invalid API responses
- ✅ Network timeouts

## DevOps Best Practices Demonstrated

1. **Environment Management** - Secure credential handling with `.env` files
## GitHub Repository

After setting up, publish to GitHub:

```bash
git add .
git commit -m "Weather Data Collection System"
git remote add origin https://github.com/YOUR_USERNAME/weather-data-collection-system.git
git push -u origin main
```

## Architecture Diagram

The complete system architecture is visualized in `architecture_diagram.png` (shown above in the Technical Architecture section).

---

**DevOps Project - Weather Data Collection System**
