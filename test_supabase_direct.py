from supabase import create_client
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Get credentials
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print("=" * 50)
print("SUPABASE CONNECTION TEST")
print("=" * 50)
print(f"URL: {url}")
print(f"KEY (first 20 chars): {key[:20] if key else 'None'}...")
print(f"KEY (last 10 chars): {key[-10:] if key and len(key) > 10 else 'None'}")

if not url or not key:
    print("\n❌ Missing URL or KEY! Check your .env file")
    exit()

try:
    print("\nAttempting to connect...")
    client = create_client(url, key)
    
    # Try a simple query
    result = client.table('employees').select('*').limit(1).execute()
    print("\n✅ CONNECTION SUCCESSFUL!")
    print(f"   Query result: {result.data}")
    
except Exception as e:
    print(f"\n❌ Connection failed: {e}")