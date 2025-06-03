import os
import requests
import base64
from openai import OpenAI
from video import Video
import config
from database import DatabaseManager
import tempfile
import json
from datetime import datetime
import yt_dlp

class VideoAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.db = DatabaseManager()
        
    def download_video(self, video_url):
        """Download video from URL using yt-dlp with fallback to direct download"""
        temp_file_path = None
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            temp_file_path = temp_file.name
            temp_file.close()
            
            # First try yt-dlp for platform videos (YouTube, Twitch, etc.)
            try:
                ydl_opts = {
                    'outtmpl': temp_file_path,
                    'format': 'best[ext=mp4]/best',
                    'noplaylist': True,
                    'extract_flat': False,
                    'quiet': True,
                    'no_warnings': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                
                # Check if file was downloaded and has content
                if os.path.exists(temp_file_path) and os.path.getsize(temp_file_path) > 0:
                    print(f"✓ Video downloaded via yt-dlp to: {temp_file_path}")
                    return temp_file_path
                else:
                    print("⚠️ yt-dlp download failed, trying direct download...")
                    
            except Exception as e:
                print(f"⚠️ yt-dlp failed ({str(e)}), trying direct download...")
            
            # Fallback to direct download for direct video file URLs
            try:
                response = requests.get(video_url, stream=True, timeout=30)
                response.raise_for_status()
                
                # Check if it's actually a video file
                content_type = response.headers.get('content-type', '').lower()
                if not any(video_type in content_type for video_type in ['video/', 'application/octet-stream']):
                    raise Exception(f"URL does not point to a video file (content-type: {content_type})")
                
                # Write video content to temp file
                with open(temp_file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                # Verify file was written and has content
                if os.path.exists(temp_file_path) and os.path.getsize(temp_file_path) > 0:
                    print(f"✓ Video downloaded via direct download to: {temp_file_path}")
                    return temp_file_path
                else:
                    raise Exception("Downloaded file is empty")
                    
            except Exception as e:
                raise Exception(f"Direct download also failed: {str(e)}")
                
        except Exception as e:
            # Clean up temp file if download failed
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
            raise Exception(f"Failed to download video: {str(e)}")
    
    def extract_audio_and_transcribe(self, video_path):
        """Extract audio from video and transcribe using OpenAI Whisper"""
        try:
            from moviepy import VideoFileClip
            
            # Extract audio from video
            video_clip = VideoFileClip(video_path)
            audio_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
            
            # Use updated moviepy parameters
            video_clip.audio.write_audiofile(audio_path, logger=None)
            video_clip.close()
            
            # Transcribe audio using OpenAI Whisper
            with open(audio_path, 'rb') as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-1",
                    response_format="verbose_json",
                    timestamp_granularities=["word"]
                )
            
            # Clean up audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            # Extract text from transcription
            if hasattr(transcription, 'words') and transcription.words:
                transcript_text = " ".join([word.word for word in transcription.words])
            else:
                transcript_text = transcription.text if hasattr(transcription, 'text') else ""
            
            return transcript_text
            
        except Exception as e:
            print(f"Warning: Failed to transcribe audio: {str(e)}")
            return ""
    
    def extract_frames(self, video_path):
        """Extract frames from video at specified intervals"""
        try:
            video = Video(video_path)
            
            # Create temp frames directory
            os.makedirs(config.TEMP_FRAMES_DIR, exist_ok=True)
            
            frames = []
            duration = int(video.duration)
            
            for t in range(0, duration, config.FRAME_STEP_TIME):
                frame_path = os.path.join(
                    config.TEMP_FRAMES_DIR, 
                    f"frame_{t}.jpg"
                )
                video.save_frame(frame_path, t)
                frames.append(frame_path)
                
                # Limit to reasonable number of frames for analysis
                if len(frames) >= 10:
                    break
            
            video.close()
            return frames
            
        except Exception as e:
            raise Exception(f"Failed to extract frames: {str(e)}")
    
    def encode_image(self, image_path):
        """Encode image to base64 for OpenAI API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_frames_with_gpt(self, frame_paths, transcript_text="", streamer_name=""):
        """
        Analyze video frames using OpenAI GPT-4 Vision with focus on streaming content
        Enhanced for streamer content analysis with transcript integration
        """
        try:
            # Encode frames to base64
            encoded_frames = []
            for frame_path in frame_paths[:5]:  # Limit to 5 frames to manage costs
                if os.path.exists(frame_path):
                    encoded_frame = self.encode_image(frame_path)
                    encoded_frames.append(encoded_frame)
            
            if not encoded_frames:
                raise Exception("No valid frames to analyze")
            
            # Build context information
            context_info = ""
            if streamer_name:
                context_info += f"This is a clip from streamer: {streamer_name}. "
            if transcript_text:
                context_info += f"Audio transcript: '{transcript_text[:500]}...' " if len(transcript_text) > 500 else f"Audio transcript: '{transcript_text}' "
            
            # Create messages for GPT-4 Vision with enhanced streaming-focused prompt
            messages = [
                {
                    "role": "system",
                    "content": f"""You are an expert streaming content analyzer specializing in Twitch/YouTube gaming and entertainment clips. Your task is to create extremely detailed, searchable descriptions focused on streaming content.

{context_info}

CRITICAL REQUIREMENTS FOR STREAMING CONTENT:

1. STREAMER IDENTIFICATION:
   - If streamer name is provided, use it
   - If not provided, try to identify the streamer from visual cues (overlays, usernames, chat, etc.)
   - Look for streamer names in chat, overlays, or UI elements
   - Note any visible usernames or channel branding

2. STREAMING CONTEXT:
   - Identify the platform (Twitch, YouTube, etc.) from UI elements
   - Describe the game being played (if gaming content)
   - Note chat interactions and viewer engagement
   - Identify stream overlays, alerts, or widgets
   - Describe the streaming setup (webcam position, background, etc.)

3. CONTENT ANALYSIS:
   - Gaming: Game title, gameplay mechanics, player actions, achievements, fails
   - Just Chatting: Topics discussed, reactions, interactions with chat
   - Creative: Art, music, cooking, etc. - describe the creative process
   - IRL: Location, activities, interactions with people

4. VISUAL DETAILS:
   - Stream layout and overlay design
   - Chat messages and viewer reactions
   - Game UI elements, menus, characters
   - Streamer's appearance, expressions, reactions
   - Background and lighting setup
   - Any on-screen text, notifications, or alerts

5. AUDIO CONTEXT (if transcript provided):
   - Integrate spoken content into description
   - Note streamer's commentary and reactions
   - Include any memorable quotes or funny moments
   - Describe interaction with chat or other players

6. SEARCHABLE TAGS:
   - Streamer name (if known)
   - Game title or category
   - Platform (twitch, youtube, etc.)
   - Content type (gaming, chatting, creative, irl)
   - Emotions (funny, epic, fail, clutch, rage, etc.)
   - Specific game elements (weapons, characters, maps, etc.)
   - Stream elements (donation, raid, host, etc.)

Return ONLY a JSON object with this exact structure:
{{
    "title": "Engaging title that captures the main streaming moment",
    "description": "Extremely detailed description including streaming context, visual elements, and transcript content",
    "tags": ["streamer_name", "game_title", "platform", "content_type", "emotions", "specific_elements"],
    "upload_date": "2025-01-31",
    "streamer": "detected_or_provided_streamer_name",
    "game": "game_title_if_gaming_content",
    "platform": "twitch/youtube/other",
    "content_type": "gaming/chatting/creative/irl",
    "transcript_included": {bool(transcript_text)}
}}"""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""Analyze these streaming video frames and provide an extremely detailed description focused on streaming content. 

{f"The streamer is: {streamer_name}" if streamer_name else "Try to identify the streamer from visual cues."}

{f"Audio transcript: {transcript_text}" if transcript_text else "No audio transcript available."}

Focus on:
- Streaming platform and setup
- Game being played (if gaming)
- Streamer reactions and commentary
- Chat interactions and viewer engagement
- Specific moments or highlights
- Visual elements unique to streaming (overlays, alerts, etc.)

Make the description searchable for streaming-specific content like game titles, streamer names, funny moments, epic plays, fails, etc."""
                        }
                    ] + [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{frame}",
                                "detail": "high"
                            }
                        } for frame in encoded_frames
                    ]
                }
            ]
            
            # Make API call to OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1200,  # Increased for more detailed streaming descriptions
                temperature=0.3   # Lower temperature for more consistent analysis
            )
            
            # Parse the response
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response
            try:
                # Remove any markdown formatting
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                result = json.loads(content)
                
                # Validate required fields
                required_fields = ["title", "description", "tags", "upload_date"]
                for field in required_fields:
                    if field not in result:
                        if field == "upload_date":
                            result["upload_date"] = datetime.now().strftime("%Y-%m-%d")
                        else:
                            raise ValueError(f"Missing required field: {field}")
                
                # Ensure tags is a list
                if not isinstance(result["tags"], list):
                    result["tags"] = []
                
                # Add transcript to description if available
                if transcript_text and len(transcript_text) > 10:
                    result["description"] += f"\n\nAudio Content: {transcript_text}"
                
                # Ensure streaming-specific fields exist
                if "streamer" not in result:
                    result["streamer"] = streamer_name if streamer_name else "Unknown"
                if "game" not in result:
                    result["game"] = "Unknown"
                if "platform" not in result:
                    result["platform"] = "Unknown"
                if "content_type" not in result:
                    result["content_type"] = "Unknown"
                if "transcript_included" not in result:
                    result["transcript_included"] = bool(transcript_text)
                
                # Add analysis metadata
                result["frames_analyzed"] = len(encoded_frames)
                result["transcript_length"] = len(transcript_text) if transcript_text else 0
                
                return result
                
            except json.JSONDecodeError as e:
                raise Exception(f"Failed to parse GPT response as JSON: {e}\nResponse: {content}")
                
        except Exception as e:
            raise Exception(f"GPT analysis failed: {str(e)}")
    
    def cleanup_temp_files(self, video_path, frame_paths):
        """Clean up temporary files"""
        try:
            # Remove video file
            if os.path.exists(video_path):
                os.remove(video_path)
            
            # Remove frame files
            for frame_path in frame_paths:
                if os.path.exists(frame_path):
                    os.remove(frame_path)
                    
        except Exception as e:
            print(f"Warning: Failed to cleanup temp files: {str(e)}")
    
    def validate_video_url(self, video_url):
        """Validate and provide helpful feedback about video URL"""
        try:
            # Check if URL is accessible
            if not video_url or not isinstance(video_url, str):
                return False, "Invalid URL format"
            
            # Check for common video platforms that yt-dlp supports
            supported_platforms = [
                'youtube.com', 'youtu.be', 'twitch.tv', 'clips.twitch.tv',
                'vimeo.com', 'dailymotion.com', 'facebook.com', 'instagram.com',
                'tiktok.com', 'twitter.com', 'x.com'
            ]
            
            # Check if it's a direct video file URL
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.m4v']
            
            url_lower = video_url.lower()
            
            # If it's a direct video file, check if accessible
            if any(ext in url_lower for ext in video_extensions):
                try:
                    response = requests.head(video_url, timeout=10)
                    if response.status_code == 200:
                        return True, "Direct video file URL"
                    elif response.status_code == 404:
                        return False, f"Video file not found (404). Please check if the URL is correct: {video_url}"
                    else:
                        return False, f"Video file not accessible (HTTP {response.status_code})"
                except requests.exceptions.RequestException as e:
                    return False, f"Cannot access video file: {str(e)}"
            
            # Check if it's a supported platform
            if any(platform in url_lower for platform in supported_platforms):
                return True, "Supported video platform"
            
            # Try to validate with yt-dlp
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'simulate': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                    if info:
                        return True, "Video URL validated by yt-dlp"
            except:
                pass
            
            return False, f"Unsupported URL. Supported: YouTube, Twitch, Vimeo, direct video files (.mp4, .avi, etc.), or other yt-dlp compatible platforms"
            
        except Exception as e:
            return False, f"URL validation error: {str(e)}"

    def analyze_video(self, video_url, streamer_name=""):
        """Main method to analyze a video from URL with streaming focus"""
        video_path = None
        frame_paths = []
        
        try:
            # Validate URL first
            is_valid, validation_message = self.validate_video_url(video_url)
            if not is_valid:
                raise ValueError(f"Invalid video URL: {validation_message}")
            
            print(f"✓ URL validated: {validation_message}")
            
            # Check if video already analyzed
            existing = self.db.get_video_by_url(video_url)
            if existing:
                print("✓ Video already analyzed, returning cached result")
                return existing
            
            print(f"🎬 Starting analysis for video: {video_url}")
            if streamer_name:
                print(f"📺 Streamer: {streamer_name}")
            
            # Download video
            print("⬇️  Downloading video...")
            video_path = self.download_video(video_url)
            
            # Extract audio and transcribe
            print("🎤 Extracting and transcribing audio...")
            transcript_text = self.extract_audio_and_transcribe(video_path)
            if transcript_text:
                print(f"📝 Transcript extracted: {len(transcript_text)} characters")
            else:
                print("⚠️  No transcript available")
            
            # Extract frames
            print("🖼️  Extracting video frames...")
            frame_paths = self.extract_frames(video_path)
            print(f"📸 Extracted {len(frame_paths)} frames")
            
            # Analyze frames with GPT
            print("🤖 Analyzing content with AI...")
            analysis = self.analyze_frames_with_gpt(frame_paths, transcript_text, streamer_name)
            
            # Save to database
            print("💾 Saving analysis to database...")
            self.db.save_video_analysis(video_url, analysis)
            
            # Return analysis with video URL
            result = analysis.copy()
            result["video_url"] = video_url
            
            print("✅ Analysis completed successfully!")
            return result
            
        except ValueError as e:
            # URL validation errors - these are user errors, not system errors
            print(f"❌ Invalid URL: {str(e)}")
            raise ValueError(str(e))
            
        except Exception as e:
            print(f"❌ Analysis failed: {str(e)}")
            
            # Provide more specific error messages
            error_msg = str(e)
            if "404" in error_msg:
                raise Exception(f"Video not found (404). Please check if the URL is correct and the video is publicly accessible: {video_url}")
            elif "403" in error_msg:
                raise Exception(f"Access denied (403). The video may be private or restricted: {video_url}")
            elif "timeout" in error_msg.lower():
                raise Exception(f"Download timeout. The video may be too large or the server is slow: {video_url}")
            elif "network" in error_msg.lower() or "connection" in error_msg.lower():
                raise Exception(f"Network error. Please check your internet connection and try again: {video_url}")
            else:
                raise Exception(f"Video analysis failed: {error_msg}")
            
        finally:
            # Cleanup temporary files
            if video_path or frame_paths:
                self.cleanup_temp_files(video_path, frame_paths)

if __name__ == "__main__":
    # Test with a sample video
    analyzer = VideoAnalyzer()
    test_url = "https://renderer.ezr.lv/render/680876b27ed09a50637439a"
    
    try:
        result = analyzer.analyze_video(test_url, streamer_name="TestStreamer")
        print("Analysis Result:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")
