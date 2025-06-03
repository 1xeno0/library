import os
import tempfile
import base64
from io import BytesIO
from PIL import Image
from moviepy.editor import VideoFileClip
import requests
import yt_dlp
from config import Config

class VideoProcessor:
    def __init__(self):
        """Initialize video processor."""
        self.temp_dir = Config.TEMP_DIR
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def download_video(self, video_url):
        """Download video from URL using yt-dlp."""
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(
                suffix='.mp4', 
                dir=self.temp_dir, 
                delete=False
            )
            temp_file.close()
            
            # Configure yt-dlp options
            ydl_opts = {
                'outtmpl': temp_file.name,
                'format': 'best[ext=mp4]/best',
                'noplaylist': True,
                'extract_flat': False,
            }
            
            # Download video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            print(f"✓ Video downloaded to: {temp_file.name}")
            return temp_file.name
            
        except Exception as e:
            print(f"✗ Error downloading video: {e}")
            # Clean up temp file if it exists
            if 'temp_file' in locals() and os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            raise
    
    def extract_frames(self, video_path, interval_seconds=None):
        """Extract frames from video at specified intervals."""
        if interval_seconds is None:
            interval_seconds = Config.FRAME_EXTRACTION_INTERVAL
        
        frames = []
        
        try:
            # Load video
            video = VideoFileClip(video_path)
            duration = video.duration
            
            print(f"✓ Video loaded. Duration: {duration:.2f} seconds")
            
            # Extract frames at intervals
            current_time = 0
            frame_count = 0
            max_frames = Config.MAX_FRAMES_FOR_ANALYSIS
            
            while current_time < duration and frame_count < max_frames:
                try:
                    # Get frame at current time
                    frame = video.get_frame(current_time)
                    
                    # Convert to PIL Image
                    pil_image = Image.fromarray(frame)
                    
                    # Convert to base64
                    buffered = BytesIO()
                    pil_image.save(buffered, format="JPEG", quality=85)
                    img_base64 = base64.b64encode(buffered.getvalue()).decode()
                    
                    frames.append({
                        'timestamp': current_time,
                        'base64': img_base64
                    })
                    
                    frame_count += 1
                    current_time += interval_seconds
                    
                except Exception as e:
                    print(f"✗ Error extracting frame at {current_time}s: {e}")
                    current_time += interval_seconds
                    continue
            
            video.close()
            print(f"✓ Extracted {len(frames)} frames")
            return frames
            
        except Exception as e:
            print(f"✗ Error processing video: {e}")
            raise
    
    def get_video_info(self, video_url):
        """Get video information using yt-dlp."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown Title'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'upload_date': info.get('upload_date', ''),
                    'view_count': info.get('view_count', 0),
                    'description': info.get('description', '')[:500]  # Limit description length
                }
                
        except Exception as e:
            print(f"✗ Error getting video info: {e}")
            return {
                'title': 'Unknown Title',
                'duration': 0,
                'uploader': 'Unknown',
                'upload_date': '',
                'view_count': 0,
                'description': ''
            }
    
    def cleanup_file(self, file_path):
        """Clean up temporary file."""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                print(f"✓ Cleaned up file: {file_path}")
        except Exception as e:
            print(f"✗ Error cleaning up file {file_path}: {e}")
    
    def cleanup_temp_files(self):
        """Clean up all temporary files."""
        try:
            for filename in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            print(f"✓ Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            print(f"✗ Error cleaning up temp directory: {e}")
    
    def validate_video_url(self, video_url):
        """Validate if the URL is a supported video URL."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'simulate': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                return info is not None
                
        except Exception:
            return False 