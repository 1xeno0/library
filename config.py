import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    # MongoDB Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'video_analysis')
    COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'videos')
    
    # Video Processing Configuration
    FRAME_EXTRACTION_INTERVAL = int(os.getenv('FRAME_EXTRACTION_INTERVAL', '5'))  # seconds
    MAX_FRAMES_FOR_ANALYSIS = int(os.getenv('MAX_FRAMES_FOR_ANALYSIS', '5'))
    TEMP_DIR = os.getenv('TEMP_DIR', './temp')
    
    # API Configuration
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', '5000'))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Video Download Configuration
    MAX_VIDEO_DURATION = int(os.getenv('MAX_VIDEO_DURATION', '3600'))  # 1 hour max
    SUPPORTED_FORMATS = ['mp4', 'avi', 'mov', 'mkv', 'webm']
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        
        # Create temp directory if it doesn't exist
        os.makedirs(cls.TEMP_DIR, exist_ok=True)
        
        return True 