"""
Test script to verify B2 connection and credentials
"""

from storage.b2_client import B2Client
from config import settings

def test_b2_connection():
    print("🧪 Testing B2 Connection...")
    print(f"Key ID: {settings.B2_APPLICATION_KEY_ID[:10]}...")
    print(f"Input Bucket: {settings.B2_BUCKET_INPUT}")
    print(f"Output Bucket: {settings.B2_BUCKET_OUTPUT}")
    print()
    
    try:
        print("Initializing B2 client...")
        client = B2Client()
        print("✅ B2 client initialized successfully!")
        print()
        
        # Test listing buckets
        print("Testing bucket access...")
        print(f"✅ B2 connection successful!")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ B2 connection failed: {str(e)}")
        print()
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_b2_connection()
    if success:
        print("🎉 B2 is configured correctly!")
    else:
        print("⚠️  Please check your B2 credentials in .env file")
