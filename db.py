import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(override=True)
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])