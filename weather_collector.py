"""
Weather Data Collection System
Fetches weather data from OpenWeather API and stores it in AWS S3
"""

import os
import json
import boto3
import requests
from datetime import datetime
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load environment variables
load_dotenv()

class WeatherCollector:
    """Handles weather data collection and storage"""
    
    def __init__(self):
        """Initialize the weather collector with API keys and AWS credentials"""
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.s3_bucket = os.getenv('S3_BUCKET_NAME')
        
        # Validate required environment variables
        self._validate_credentials()
        
        # Initialize AWS S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.aws_region
        )
        
        # OpenWeather API base URL
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    def _validate_credentials(self):
        """Validate that all required credentials are present"""
        required_vars = {
            'OPENWEATHER_API_KEY': self.api_key,
            'AWS_ACCESS_KEY_ID': self.aws_access_key,
            'AWS_SECRET_ACCESS_KEY': self.aws_secret_key,
            'S3_BUCKET_NAME': self.s3_bucket
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        
        if missing_vars:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                "Please check your .env file."
            )
    
    def fetch_weather_data(self, city):
        """
        Fetch weather data for a specific city from OpenWeather API
        
        Args:
            city (str): Name of the city
            
        Returns:
            dict: Weather data or None if request fails
        """
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'imperial'  # Fahrenheit
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant weather information
            weather_info = {
                'city': city,
                'timestamp': datetime.now().isoformat(),
                'temperature_f': data['main']['temp'],
                'feels_like_f': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'weather_condition': data['weather'][0]['main'],
                'weather_description': data['weather'][0]['description'],
                'wind_speed_mph': data['wind']['speed'],
                'country': data['sys']['country'],
                'latitude': data['coord']['lat'],
                'longitude': data['coord']['lon']
            }
            
            print(f"✓ Successfully fetched weather data for {city}")
            return weather_info
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching weather data for {city}: {str(e)}")
            return None
        except KeyError as e:
            print(f"✗ Error parsing weather data for {city}: Missing key {str(e)}")
            return None
    
    def upload_to_s3(self, data, filename):
        """
        Upload weather data to AWS S3 bucket
        
        Args:
            data (dict): Weather data to upload
            filename (str): Name of the file in S3
            
        Returns:
            bool: True if upload successful, False otherwise
        """
        try:
            json_data = json.dumps(data, indent=2)
            
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=filename,
                Body=json_data,
                ContentType='application/json'
            )
            
            print(f"✓ Successfully uploaded {filename} to S3 bucket: {self.s3_bucket}")
            return True
            
        except ClientError as e:
            print(f"✗ Error uploading to S3: {str(e)}")
            return False
        except Exception as e:
            print(f"✗ Unexpected error during S3 upload: {str(e)}")
            return False
    
    def collect_and_store(self, cities):
        """
        Collect weather data for multiple cities and store in S3
        
        Args:
            cities (list): List of city names
        """
        print(f"\n{'='*60}")
        print("Weather Data Collection System - Starting")
        print(f"{'='*60}\n")
        
        all_weather_data = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for city in cities:
            print(f"\nProcessing: {city}")
            weather_data = self.fetch_weather_data(city)
            
            if weather_data:
                all_weather_data.append(weather_data)
                
                # Display weather information
                print(f"  Temperature: {weather_data['temperature_f']:.1f}°F")
                print(f"  Feels Like: {weather_data['feels_like_f']:.1f}°F")
                print(f"  Humidity: {weather_data['humidity']}%")
                print(f"  Condition: {weather_data['weather_description'].title()}")
        
        # Upload combined data to S3
        if all_weather_data:
            print(f"\n{'-'*60}")
            print("Uploading data to AWS S3...")
            print(f"{'-'*60}\n")
            
            filename = f"weather_data_{timestamp}.json"
            self.upload_to_s3(all_weather_data, filename)
            
            # Also save locally for backup
            local_filename = f"weather_data_backup_{timestamp}.json"
            with open(local_filename, 'w') as f:
                json.dump(all_weather_data, f, indent=2)
            print(f"✓ Local backup saved: {local_filename}")
        
        print(f"\n{'='*60}")
        print(f"Collection Complete - Processed {len(all_weather_data)}/{len(cities)} cities")
        print(f"{'='*60}\n")


def main():
    """Main execution function"""
    # List of cities to track
    cities = [
        'New York',
        'Los Angeles',
        'Chicago',
        'Houston',
        'Phoenix',
        'London',
        'Tokyo',
        'Paris'
    ]
    
    try:
        collector = WeatherCollector()
        collector.collect_and_store(cities)
    except EnvironmentError as e:
        print(f"\n❌ Configuration Error: {str(e)}")
        print("\nPlease ensure your .env file contains:")
        print("  - OPENWEATHER_API_KEY")
        print("  - AWS_ACCESS_KEY_ID")
        print("  - AWS_SECRET_ACCESS_KEY")
        print("  - S3_BUCKET_NAME")
        print("  - AWS_REGION (optional, defaults to us-east-1)")
    except Exception as e:
        print(f"\n❌ Unexpected Error: {str(e)}")


if __name__ == "__main__":
    main()
