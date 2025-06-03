import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = ""

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "s")

# Frame extraction settings
FRAME_STEP_TIME = 5  # Extract frame every 5 seconds
TEMP_FRAMES_DIR = "temp/frames"
TEMP_VIDEOS_DIR = "temp/videos"

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = int(os.getenv("PORT", 5555))
DEBUG = True

