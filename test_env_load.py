from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env
env_file = Path('.env')
print(f"Looking for .env at: {env_file.absolute()}")
print(f"File exists: {env_file.exists()}")

if env_file.exists():
    load_dotenv()
    print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
    print(f"SUPABASE_KEY: {os.getenv('SUPABASE_KEY')[:20]}...")
else:
    print("❌ .env file not found!")