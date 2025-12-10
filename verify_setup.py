"""
Verification and Testing Script
This script helps you verify that all components of the Weather Data Collection System are working correctly
"""

import os
import sys
from dotenv import load_dotenv
import requests
import json

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def test_python_version():
    """Test 1: Verify Python version"""
    print_header("TEST 1: Python Version")
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 7:
        print_success(f"Python {version.major}.{version.minor} is compatible")
        return True
    else:
        print_error(f"Python 3.7+ required. You have {version.major}.{version.minor}")
        return False

def test_environment_file():
    """Test 2: Check if .env file exists and is configured"""
    print_header("TEST 2: Environment File (.env)")
    
    if not os.path.exists('.env'):
        print_error(".env file not found!")
        print_info("Create .env file by copying .env.example:")
        print_info("  copy .env.example .env")
        print_info("Then edit .env with your actual credentials")
        return False
    
    print_success(".env file exists")
    
    # Load and check variables
    load_dotenv()
    
    required_vars = {
        'OPENWEATHER_API_KEY': os.getenv('OPENWEATHER_API_KEY'),
        'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'S3_BUCKET_NAME': os.getenv('S3_BUCKET_NAME'),
        'AWS_REGION': os.getenv('AWS_REGION', 'us-east-1')
    }
    
    all_configured = True
    for var_name, var_value in required_vars.items():
        if not var_value or 'your_' in var_value.lower() or 'here' in var_value.lower():
            print_error(f"{var_name} is not configured")
            all_configured = False
        else:
            # Mask the value for security
            masked = var_value[:4] + '*' * (len(var_value) - 8) + var_value[-4:] if len(var_value) > 8 else '****'
            print_success(f"{var_name} = {masked}")
    
    if not all_configured:
        print_warning("Please configure all environment variables in .env file")
        return False
    
    return True

def test_dependencies():
    """Test 3: Check if all required packages are installed"""
    print_header("TEST 3: Python Dependencies")
    
    required_packages = {
        'boto3': 'AWS SDK',
        'requests': 'HTTP Library',
        'dotenv': 'Environment Variables',
        'botocore': 'AWS Core Library'
    }
    
    all_installed = True
    for package, description in required_packages.items():
        try:
            if package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print_success(f"{package} ({description}) is installed")
        except ImportError:
            print_error(f"{package} ({description}) is NOT installed")
            all_installed = False
    
    if not all_installed:
        print_warning("Install missing packages:")
        print_info("  pip install -r requirements.txt")
        return False
    
    return True

def test_openweather_api():
    """Test 4: Test OpenWeather API connection"""
    print_header("TEST 4: OpenWeather API Connection")
    
    load_dotenv()
    api_key = os.getenv('OPENWEATHER_API_KEY')
    
    if not api_key:
        print_error("OPENWEATHER_API_KEY not found in .env")
        return False
    
    print_info("Testing API connection with London...")
    
    try:
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': 'London',
            'appid': api_key,
            'units': 'imperial'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success("OpenWeather API is working!")
            print(f"  Location: {data['name']}, {data['sys']['country']}")
            print(f"  Temperature: {data['main']['temp']}°F")
            print(f"  Condition: {data['weather'][0]['description'].title()}")
            print(f"  Humidity: {data['main']['humidity']}%")
            return True
        elif response.status_code == 401:
            print_error("Invalid API key!")
            print_info("Get your API key from: https://openweathermap.org/api")
            print_info("It may take 10 minutes to activate after creation")
            return False
        else:
            print_error(f"API returned status code: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Connection timeout! Check your internet connection")
        return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to OpenWeather API! Check your internet")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return False

def test_aws_credentials():
    """Test 5: Test AWS credentials"""
    print_header("TEST 5: AWS Credentials")
    
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
        
        load_dotenv()
        
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        
        print_info("Testing AWS credentials...")
        
        # Try to list buckets (this verifies credentials)
        try:
            response = s3_client.list_buckets()
            print_success("AWS credentials are valid!")
            print(f"  You have access to {len(response['Buckets'])} bucket(s)")
            
            bucket_name = os.getenv('S3_BUCKET_NAME')
            bucket_exists = any(b['Name'] == bucket_name for b in response['Buckets'])
            
            if bucket_exists:
                print_success(f"Bucket '{bucket_name}' exists and is accessible")
            else:
                print_warning(f"Bucket '{bucket_name}' not found")
                print_info("Run: python infrastructure_setup.py")
                print_info("Or create bucket manually in AWS Console")
            
            return bucket_exists
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'InvalidAccessKeyId':
                print_error("Invalid AWS Access Key ID!")
            elif error_code == 'SignatureDoesNotMatch':
                print_error("Invalid AWS Secret Access Key!")
            else:
                print_error(f"AWS Error: {error_code}")
            print_info("Check your AWS credentials in .env file")
            return False
            
    except NoCredentialsError:
        print_error("AWS credentials not found!")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return False

def test_s3_write_access():
    """Test 6: Test S3 write access"""
    print_header("TEST 6: S3 Write Access")
    
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        load_dotenv()
        bucket_name = os.getenv('S3_BUCKET_NAME')
        
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        
        print_info(f"Testing write access to bucket: {bucket_name}")
        
        # Try to upload a test file
        test_data = json.dumps({
            'test': 'verification',
            'timestamp': '2025-12-10',
            'status': 'testing'
        })
        
        test_key = 'verification_test.json'
        
        try:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=test_key,
                Body=test_data,
                ContentType='application/json'
            )
            print_success("Successfully wrote test file to S3!")
            
            # Clean up test file
            s3_client.delete_object(Bucket=bucket_name, Key=test_key)
            print_success("Test file cleaned up")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                print_error(f"Bucket '{bucket_name}' does not exist!")
                print_info("Run: python infrastructure_setup.py")
            elif error_code == 'AccessDenied':
                print_error("Access Denied! Check IAM permissions")
                print_info("Your IAM user needs 's3:PutObject' permission")
            else:
                print_error(f"S3 Error: {error_code}")
            return False
            
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return False

def test_main_application():
    """Test 7: Check main application file"""
    print_header("TEST 7: Main Application File")
    
    if not os.path.exists('weather_collector.py'):
        print_error("weather_collector.py not found!")
        return False
    
    print_success("weather_collector.py exists")
    
    # Check file size
    size = os.path.getsize('weather_collector.py')
    print_success(f"File size: {size} bytes ({size // 1024} KB)")
    
    # Try to import it (syntax check)
    try:
        import weather_collector
        print_success("No syntax errors found")
        return True
    except SyntaxError as e:
        print_error(f"Syntax error in weather_collector.py: {str(e)}")
        return False
    except Exception as e:
        # ImportError is expected if dependencies aren't met
        print_warning(f"Note: {str(e)}")
        return True

def run_quick_test():
    """Test 8: Run a quick end-to-end test"""
    print_header("TEST 8: Quick End-to-End Test")
    
    print_info("This will fetch weather for one city and test S3 upload...")
    
    try:
        from weather_collector import WeatherCollector
        
        collector = WeatherCollector()
        
        # Test with one city
        print_info("Fetching weather data for New York...")
        weather_data = collector.fetch_weather_data('New York')
        
        if weather_data:
            print_success("Successfully fetched weather data!")
            print(f"  Temperature: {weather_data['temperature_f']}°F")
            print(f"  Condition: {weather_data['weather_description']}")
            
            # Test S3 upload
            print_info("Testing S3 upload...")
            test_filename = 'verification_weather_test.json'
            if collector.upload_to_s3([weather_data], test_filename):
                print_success("Successfully uploaded to S3!")
                
                # Clean up
                try:
                    collector.s3_client.delete_object(
                        Bucket=collector.s3_bucket,
                        Key=test_filename
                    )
                    print_success("Cleaned up test file from S3")
                except:
                    pass
                
                return True
            else:
                print_error("S3 upload failed")
                return False
        else:
            print_error("Failed to fetch weather data")
            return False
            
    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return False

def print_summary(results):
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    print(f"Total Tests: {total}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
    print(f"{Colors.RED}Failed: {failed}{Colors.END}")
    print(f"Success Rate: {(passed/total)*100:.1f}%\n")
    
    if failed == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! System is ready to use!{Colors.END}")
        print(f"\n{Colors.BLUE}Run the main application:{Colors.END}")
        print(f"  python weather_collector.py\n")
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠ Some tests failed. Please fix the issues above.{Colors.END}\n")
        
        # Provide specific guidance
        if not results.get('Environment File'):
            print_info("Step 1: Configure your .env file")
            print("  copy .env.example .env")
            print("  Then edit .env with your credentials\n")
        
        if not results.get('Dependencies'):
            print_info("Step 2: Install dependencies")
            print("  pip install -r requirements.txt\n")
        
        if not results.get('OpenWeather API'):
            print_info("Step 3: Get OpenWeather API key")
            print("  Visit: https://openweathermap.org/api\n")
        
        if not results.get('AWS Credentials'):
            print_info("Step 4: Configure AWS credentials")
            print("  Visit: AWS Console → IAM → Users → Security Credentials\n")
        
        if not results.get('S3 Bucket Exists'):
            print_info("Step 5: Create S3 bucket")
            print("  python infrastructure_setup.py\n")

def main():
    """Main verification function"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║        Weather Data Collection System - Verification Tool        ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    print("\nThis tool will verify that your system is properly configured.\n")
    
    # Run all tests
    results = {}
    
    results['Python Version'] = test_python_version()
    results['Environment File'] = test_environment_file()
    results['Dependencies'] = test_dependencies()
    
    # Only run API tests if basic setup is complete
    if results['Environment File'] and results['Dependencies']:
        results['OpenWeather API'] = test_openweather_api()
        results['AWS Credentials'] = test_aws_credentials()
        
        if results['AWS Credentials']:
            results['S3 Bucket Exists'] = results['AWS Credentials']
            results['S3 Write Access'] = test_s3_write_access()
    
    results['Main Application'] = test_main_application()
    
    # Run end-to-end test if all basic tests passed
    if all([results.get('Environment File'), results.get('Dependencies'), 
            results.get('OpenWeather API'), results.get('S3 Write Access')]):
        results['End-to-End Test'] = run_quick_test()
    
    # Print summary
    print_summary(results)
    
    return all(results.values())

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Verification cancelled by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.RED}Unexpected error: {str(e)}{Colors.END}")
        sys.exit(1)
