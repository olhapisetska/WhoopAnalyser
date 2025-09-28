import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("WHOOP_CLIENT_ID")
CLIENT_SECRET = os.getenv("WHOOP_CLIENT_SECRET")
USERNAME = os.getenv("WHOOP_USERNAME")
PASSWORD = os.getenv("WHOOP_PASSWORD")
REDIRECT_URI=os.getenv("WHOOP_REDIRECT_URI")
