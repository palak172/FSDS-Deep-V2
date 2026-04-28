import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Get the directory where THIS script is located
script_dir = Path(__file__).parent
env_path = script_dir / '.env'

print(f"Looking for .env at: {env_path}")
print(f"File exists: {env_path.exists()}")

load_dotenv(dotenv_path=env_path, encoding='utf-8')

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"URL: {url}")
print(f"Key exists: {bool(key)}")

if url and key:
    try:
        client = create_client(url, key)
        print("✅ Connected!")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("❌ Missing URL or KEY")