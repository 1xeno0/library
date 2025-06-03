import openai
import json
from datetime import datetime
from database import DatabaseManager
from video import VideoProcessor
from config import Config

class VideoAnalyzer:
    def __init__(self):
        """Initialize video analyzer."""
        # Validate configuration
        Config.validate_config()
        
        # Initialize OpenAI client
        openai.api_key = Config.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Initialize components
        self.db = DatabaseManager()
        self.video_processor = VideoProcessor()
        
        print("✓ VideoAnalyzer initialized successfully")
    
    def analyze_video(self, video_url):
        """Analyze video content using OpenAI."""
        try:
            print(f"🎬 Starting analysis for: {video_url}")
            
            # Check if video already exists in database
            existing_video = self.db.find_video_by_url(video_url)
            if existing_video:
                print("✓ Video already analyzed, returning cached result")
                return self._format_response(existing_video)
            
            # Validate video URL
            if not self.video_processor.validate_video_url(video_url):
                raise ValueError("Invalid or unsupported video URL")
            
            # Get video information
            video_info = self.video_processor.get_video_info(video_url)
            print(f"✓ Video info retrieved: {video_info['title']}")
            
            # Download video
            video_path = self.video_processor.download_video(video_url)
            
            try:
                # Extract frames
                frames = self.video_processor.extract_frames(video_path)
                
                if not frames:
                    raise ValueError("No frames could be extracted from video")
                
                # Analyze frames with OpenAI
                analysis_result = self._analyze_frames_with_openai(frames, video_info)
                
                # Prepare data for database
                video_data = {
                    'video_url': video_url,
                    'title': analysis_result.get('title', video_info['title']),
                    'description': analysis_result.get('description', video_info['description']),
                    'tags': analysis_result.get('tags', []),
                    'upload_date': video_info['upload_date'],
                    'duration': video_info['duration'],
                    'uploader': video_info['uploader'],
                    'view_count': video_info['view_count'],
                    'analysis_timestamp': datetime.utcnow().isoformat(),
                    'frame_count': len(frames)
                }
                
                # Save to database
                self.db.save_video_analysis(video_data)
                
                print("✅ Video analysis completed successfully")
                return self._format_response(video_data)
                
            finally:
                # Clean up downloaded video file
                self.video_processor.cleanup_file(video_path)
                
        except Exception as e:
            print(f"❌ Error analyzing video: {e}")
            raise
    
    def _analyze_frames_with_openai(self, frames, video_info):
        """Analyze extracted frames using OpenAI Vision API."""
        try:
            print(f"🤖 Analyzing {len(frames)} frames with OpenAI...")
            
            # Prepare messages for OpenAI
            messages = [
                {
                    "role": "system",
                    "content": """You are a video content analyzer. Analyze the provided video frames and return a JSON response with:
                    - title: A descriptive title for the video content
                    - description: A detailed description of what's happening in the video
                    - tags: An array of relevant tags/keywords (5-10 tags)
                    
                    Focus on identifying:
                    - Main subjects/objects in the video
                    - Activities or actions taking place
                    - Setting/environment
                    - Any text or graphics visible
                    - Overall theme or category
                    
                    Return only valid JSON format."""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Analyze this video. Original title: '{video_info['title']}'. Please provide analysis based on the frames:"
                        }
                    ]
                }
            ]
            
            # Add frame images to the message
            for i, frame in enumerate(frames[:Config.MAX_FRAMES_FOR_ANALYSIS]):
                messages[1]["content"].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{frame['base64']}",
                        "detail": "low"  # Use low detail to reduce costs
                    }
                })
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=messages,
                max_tokens=1000,
                temperature=0.3
            )
            
            # Parse response
            content = response.choices[0].message.content
            
            try:
                analysis_result = json.loads(content)
                print("✓ OpenAI analysis completed successfully")
                return analysis_result
            except json.JSONDecodeError:
                print("⚠️ OpenAI response was not valid JSON, using fallback")
                return self._create_fallback_analysis(video_info, content)
                
        except Exception as e:
            print(f"✗ Error in OpenAI analysis: {e}")
            return self._create_fallback_analysis(video_info)
    
    def _create_fallback_analysis(self, video_info, ai_content=None):
        """Create fallback analysis when OpenAI fails."""
        return {
            'title': video_info['title'],
            'description': ai_content if ai_content else video_info['description'],
            'tags': ['video', 'content', 'media']
        }
    
    def _format_response(self, video_data):
        """Format response for API."""
        return {
            'success': True,
            'data': {
                'video_url': video_data['video_url'],
                'title': video_data['title'],
                'description': video_data['description'],
                'tags': video_data['tags'],
                'upload_date': video_data.get('upload_date', ''),
                'duration': video_data.get('duration', 0),
                'uploader': video_data.get('uploader', ''),
                'analysis_timestamp': video_data.get('analysis_timestamp', ''),
                'frame_count': video_data.get('frame_count', 0)
            }
        }
    
    def search_videos(self, query=None, tags=None):
        """Search videos in database."""
        try:
            results = self.db.search_videos(query=query, tags=tags)
            
            formatted_results = []
            for video in results:
                formatted_results.append({
                    'video_url': video['video_url'],
                    'title': video['title'],
                    'description': video['description'],
                    'tags': video['tags'],
                    'upload_date': video.get('upload_date', ''),
                    'duration': video.get('duration', 0),
                    'uploader': video.get('uploader', ''),
                    'created_at': video.get('created_at', '').isoformat() if video.get('created_at') else ''
                })
            
            return {
                'success': True,
                'count': len(formatted_results),
                'data': formatted_results
            }
            
        except Exception as e:
            print(f"❌ Error searching videos: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': []
            }
    
    def get_all_videos(self):
        """Get all videos from database."""
        try:
            results = self.db.get_all_videos()
            
            formatted_results = []
            for video in results:
                formatted_results.append({
                    'video_url': video['video_url'],
                    'title': video['title'],
                    'description': video['description'],
                    'tags': video['tags'],
                    'upload_date': video.get('upload_date', ''),
                    'duration': video.get('duration', 0),
                    'uploader': video.get('uploader', ''),
                    'created_at': video.get('created_at', '').isoformat() if video.get('created_at') else ''
                })
            
            return {
                'success': True,
                'count': len(formatted_results),
                'data': formatted_results
            }
            
        except Exception as e:
            print(f"❌ Error getting all videos: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': []
            } 