"""
Video processing utilities using MoviePy
"""

from moviepy import VideoFileClip
import os

class Video:
    """Simple wrapper around MoviePy for video operations"""
    
    def __init__(self, video_path):
        """Initialize video from file path"""
        self.video_path = video_path
        self.clip = VideoFileClip(video_path)
        self.duration = self.clip.duration
    
    def save_frame(self, output_path, time_seconds):
        """Save a frame at the specified time to output path"""
        try:
            # Ensure the time is within video duration
            if time_seconds > self.duration:
                time_seconds = self.duration - 1
            
            # Extract frame at specified time
            frame = self.clip.get_frame(time_seconds)
            
            # Save frame as image
            from PIL import Image
            img = Image.fromarray(frame)
            img.save(output_path, 'JPEG')
            
        except Exception as e:
            raise Exception(f"Failed to save frame at {time_seconds}s: {str(e)}")
    
    def close(self):
        """Close the video clip and free resources"""
        if hasattr(self, 'clip') and self.clip:
            self.clip.close()
    
    def __del__(self):
        """Destructor to ensure resources are freed"""
        self.close()

    def cut(self, start, end=None):
        return self.clip.subclip(start, end)

    def extract_frames(self, interval=5, output_dir="temp/frames"):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for t in range(0, int(self.duration), interval):
            self.save_frame(output_dir + "/" + self.video_path.split("/")[-1].split(".")[0] + f"_frame_{t}.jpg", t)


if __name__ == "__main__":
    video = Video("clips/kci.mp4")
    video.extract_frames()