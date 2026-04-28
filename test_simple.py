# save as test_simple.py
from dotenv import load_dotenv
import os

load_dotenv()
print(f"URL: {os.getenv('SUPABASE_URL')}")
print(f"KEY: {os.getenv('SUPABASE_KEY')[:20] if os.getenv('SUPABASE_KEY') else 'None'}...")