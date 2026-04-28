import os
from pathlib import Path
from dotenv import load_dotenv

print("=" * 50)
print("ENVIRONMENT DIAGNOSTIC")
print("=" * 50)

# Check current working directory
print(f"Current directory: {Path.cwd()}")

# Check if .env file exists
env_file = Path.cwd() / '.env'
print(f".env file path: {env_file}")
print(f".env file exists: {env_file.exists()}")

if env_file.exists():
    # Read the file content
    with open(env_file, 'r') as f:
        content = f.read()
        print(f"\n.env file content:\n{content}")
else:
    print("\n❌ .env file NOT found!")

# Try to load it
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"\nSUPABASE_URL loaded: {'✅' if url else '❌'}")
print(f"SUPABASE_KEY loaded: {'✅' if key else '❌'}")

if url:
    print(f"URL value: {url}")
if key:
    print(f"KEY value (first 20 chars): {key[:20]}...")