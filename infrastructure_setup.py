"""
Infrastructure as Code (IaC) - AWS S3 Bucket Setup
This script demonstrates Infrastructure as Code principles by automating AWS resource creation
"""

import boto3
import json
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()

class InfrastructureManager:
    """Manages AWS infrastructure setup and configuration"""
    
    def __init__(self):
        """Initialize AWS clients"""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.region = os.getenv('AWS_REGION', 'us-east-1')
    
    def create_s3_bucket(self, bucket_name):
        """
        Create S3 bucket for weather data storage
        
        Args:
            bucket_name (str): Name of the bucket to create
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.region == 'us-east-1':
                # us-east-1 requires different creation syntax
                self.s3_client.create_bucket(Bucket=bucket_name)
            else:
                self.s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )
            
            print(f"✓ Successfully created S3 bucket: {bucket_name}")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                print(f"ℹ Bucket {bucket_name} already exists and is owned by you")
                return True
            else:
                print(f"✗ Error creating bucket: {e}")
                return False
    
    def configure_bucket_versioning(self, bucket_name):
        """
        Enable versioning on S3 bucket for data tracking
        
        Args:
            bucket_name (str): Name of the bucket
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.s3_client.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            print(f"✓ Enabled versioning on bucket: {bucket_name}")
            return True
        except ClientError as e:
            print(f"✗ Error enabling versioning: {e}")
            return False
    
    def set_bucket_lifecycle_policy(self, bucket_name, days_to_archive=90):
        """
        Set lifecycle policy to archive old data
        
        Args:
            bucket_name (str): Name of the bucket
            days_to_archive (int): Days before archiving to Glacier
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            lifecycle_policy = {
                'Rules': [
                    {
                        'Id': 'Archive old weather data',
                        'Status': 'Enabled',
                        'Prefix': 'weather_data_',
                        'Transitions': [
                            {
                                'Days': days_to_archive,
                                'StorageClass': 'GLACIER'
                            }
                        ]
                    }
                ]
            }
            
            self.s3_client.put_bucket_lifecycle_configuration(
                Bucket=bucket_name,
                LifecycleConfiguration=lifecycle_policy
            )
            print(f"✓ Set lifecycle policy: Archive after {days_to_archive} days")
            return True
        except ClientError as e:
            print(f"✗ Error setting lifecycle policy: {e}")
            return False
    
    def add_bucket_tags(self, bucket_name):
        """
        Add tags to bucket for organization and billing
        
        Args:
            bucket_name (str): Name of the bucket
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            tags = {
                'TagSet': [
                    {'Key': 'Project', 'Value': 'WeatherDataCollection'},
                    {'Key': 'Environment', 'Value': 'Production'},
                    {'Key': 'ManagedBy', 'Value': 'InfrastructureAsCode'},
                    {'Key': 'Purpose', 'Value': 'WeatherDataStorage'},
                    {'Key': 'DataType', 'Value': 'JSON'}
                ]
            }
            
            self.s3_client.put_bucket_tagging(
                Bucket=bucket_name,
                Tagging=tags
            )
            print(f"✓ Added tags to bucket: {bucket_name}")
            return True
        except ClientError as e:
            print(f"✗ Error adding tags: {e}")
            return False
    
    def verify_bucket_access(self, bucket_name):
        """
        Verify that we can access and write to the bucket
        
        Args:
            bucket_name (str): Name of the bucket
            
        Returns:
            bool: True if accessible, False otherwise
        """
        try:
            # Try to list objects
            self.s3_client.head_bucket(Bucket=bucket_name)
            print(f"✓ Bucket {bucket_name} is accessible")
            
            # Try to put a test object
            test_key = 'infrastructure_test.json'
            test_data = json.dumps({'test': 'Infrastructure verification'})
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=test_key,
                Body=test_data
            )
            print(f"✓ Write access verified")
            
            # Clean up test object
            self.s3_client.delete_object(Bucket=bucket_name, Key=test_key)
            print(f"✓ Bucket configuration complete")
            
            return True
        except ClientError as e:
            print(f"✗ Bucket access verification failed: {e}")
            return False
    
    def get_bucket_info(self, bucket_name):
        """
        Get information about the bucket
        
        Args:
            bucket_name (str): Name of the bucket
        """
        try:
            # Get bucket location
            location = self.s3_client.get_bucket_location(Bucket=bucket_name)
            print(f"\nBucket Information:")
            print(f"  Name: {bucket_name}")
            print(f"  Region: {location['LocationConstraint'] or 'us-east-1'}")
            
            # Get versioning status
            versioning = self.s3_client.get_bucket_versioning(Bucket=bucket_name)
            print(f"  Versioning: {versioning.get('Status', 'Disabled')}")
            
            # Get tags
            try:
                tags = self.s3_client.get_bucket_tagging(Bucket=bucket_name)
                print(f"  Tags: {len(tags['TagSet'])} tags applied")
            except ClientError:
                print(f"  Tags: None")
            
            # List recent objects
            objects = self.s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=5)
            if 'Contents' in objects:
                print(f"  Objects: {objects['KeyCount']} (showing up to 5)")
                for obj in objects['Contents']:
                    print(f"    - {obj['Key']} ({obj['Size']} bytes)")
            else:
                print(f"  Objects: 0 (empty bucket)")
                
        except ClientError as e:
            print(f"✗ Error getting bucket info: {e}")
    
    def setup_complete_infrastructure(self, bucket_name):
        """
        Complete infrastructure setup with all configurations
        
        Args:
            bucket_name (str): Name of the bucket to set up
        """
        print(f"\n{'='*60}")
        print("Infrastructure as Code - AWS S3 Setup")
        print(f"{'='*60}\n")
        
        steps = [
            ("Creating S3 bucket", lambda: self.create_s3_bucket(bucket_name)),
            ("Enabling versioning", lambda: self.configure_bucket_versioning(bucket_name)),
            ("Adding tags", lambda: self.add_bucket_tags(bucket_name)),
            ("Setting lifecycle policy", lambda: self.set_bucket_lifecycle_policy(bucket_name)),
            ("Verifying access", lambda: self.verify_bucket_access(bucket_name))
        ]
        
        success_count = 0
        for step_name, step_func in steps:
            print(f"\n{step_name}...")
            if step_func():
                success_count += 1
        
        print(f"\n{'='*60}")
        print(f"Infrastructure Setup Complete: {success_count}/{len(steps)} steps successful")
        print(f"{'='*60}\n")
        
        # Display bucket info
        self.get_bucket_info(bucket_name)


def main():
    """Main execution function"""
    print("\n🏗️  Infrastructure as Code - AWS S3 Setup\n")
    
    # Get bucket name from environment or use default
    bucket_name = os.getenv('S3_BUCKET_NAME')
    
    if not bucket_name:
        print("⚠️  S3_BUCKET_NAME not set in .env file")
        print("Using default bucket name pattern...")
        import random
        bucket_name = f"weather-data-{random.randint(1000, 9999)}"
        print(f"Suggested bucket name: {bucket_name}")
        print("\nPlease add this to your .env file:")
        print(f"S3_BUCKET_NAME={bucket_name}")
        response = input("\nProceed with this bucket name? (y/n): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    try:
        manager = InfrastructureManager()
        manager.setup_complete_infrastructure(bucket_name)
        
        print("\n✅ Infrastructure is ready!")
        print(f"You can now run: python weather_collector.py")
        
    except Exception as e:
        print(f"\n❌ Infrastructure setup failed: {e}")
        print("\nPlease check:")
        print("  1. AWS credentials are correct in .env")
        print("  2. IAM user has S3 permissions")
        print("  3. Bucket name is globally unique")


if __name__ == "__main__":
    main()
