from flask import Flask, request, jsonify
from flask_cors import CORS
import config
from analyse import VideoAnalyzer
from database import DatabaseManager
import traceback
import json
import uuid
from datetime import datetime
import threading
import time

app = Flask(__name__)
CORS(app)

# Initialize components
analyzer = VideoAnalyzer()
db = DatabaseManager()

# Store for tracking analysis progress
analysis_progress = {}

@app.route('/analyse', methods=['POST'])
def analyse_video():
    """
    POST /analyse
    Analyzes a video from the provided URL and returns metadata with streaming focus
    
    Request body:
    {
        "video_link": "https://renderer.ezr.lv/render/680876b27ed09a50637439a",
        "streamer_name": "optional_streamer_name"
    }
    
    Response:
    {
        "title": "Epic Gaming Moment - Streamer Clutch Play",
        "description": "Detailed description including streaming context and transcript",
        "tags": ["gaming", "clutch", "streamer_name", "epic"],
        "upload_date": "2025-01-31",
        "streamer": "streamer_name",
        "game": "game_title",
        "platform": "twitch",
        "content_type": "gaming",
        "transcript_included": true
    }
    """
    try:
        # Get request data with proper JSON error handling
        try:
            data = request.get_json()
        except Exception as e:
            return jsonify({
                "error": "Invalid JSON format"
            }), 400
        
        if not data or 'video_link' not in data:
            return jsonify({
                "error": "Missing required field 'video_link'"
            }), 400
        
        video_url = data['video_link']
        streamer_name = data.get('streamer_name', '')  # Optional streamer name
        
        if not video_url:
            return jsonify({
                "error": "video_link cannot be empty"
            }), 400
        
        print(f"🎬 Analyzing video: {video_url}")
        if streamer_name:
            print(f"📺 Streamer: {streamer_name}")
        
        # Analyze the video with streaming focus
        result = analyzer.analyze_video(video_url, streamer_name)
        
        # Return enhanced streaming analysis
        response = {
            "title": result.get("title", ""),
            "description": result.get("description", ""),
            "tags": result.get("tags", []),
            "upload_date": result.get("upload_date", ""),
            "streamer": result.get("streamer", "Unknown"),
            "game": result.get("game", "Unknown"),
            "platform": result.get("platform", "Unknown"),
            "content_type": result.get("content_type", "Unknown"),
            "transcript_included": result.get("transcript_included", False),
            "frames_analyzed": result.get("frames_analyzed", 0),
            "transcript_length": result.get("transcript_length", 0),
            "video_url": video_url
        }
        
        return jsonify(response), 200
        
    except ValueError as e:
        # URL validation errors - these are client errors (400)
        print(f"❌ Invalid URL: {str(e)}")
        return jsonify({
            "error": f"Invalid video URL: {str(e)}"
        }), 400
        
    except Exception as e:
        # Other errors - these are server errors (500)
        print(f"❌ Error in /analyse: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "error": f"Analysis failed: {str(e)}"
        }), 500

@app.route('/analyse/batch', methods=['POST'])
def analyse_batch():
    """
    POST /analyse/batch
    Start batch analysis of multiple clips and return job ID for tracking
    
    Request body:
    {
        "clips": [
            {"video_link": "url1", "streamer_name": "streamer1"},
            {"video_link": "url2", "streamer_name": "streamer2"}
        ]
    }
    
    Response:
    {
        "job_id": "uuid",
        "total_clips": 5,
        "status": "started"
    }
    """
    try:
        data = request.get_json()
        if not data or 'clips' not in data:
            return jsonify({"error": "Missing 'clips' field"}), 400
        
        clips = data['clips']
        if not isinstance(clips, list) or len(clips) == 0:
            return jsonify({"error": "Clips must be a non-empty array"}), 400
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Initialize progress tracking
        analysis_progress[job_id] = {
            "status": "started",
            "total": len(clips),
            "completed": 0,
            "failed": 0,
            "results": [],
            "errors": [],
            "started_at": datetime.now().isoformat()
        }
        
        # Start batch analysis in background thread
        def run_batch_analysis():
            for i, clip in enumerate(clips):
                try:
                    video_url = clip.get('video_link', '')
                    streamer_name = clip.get('streamer_name', '')
                    
                    if not video_url:
                        analysis_progress[job_id]["errors"].append(f"Clip {i+1}: Missing video_link")
                        analysis_progress[job_id]["failed"] += 1
                        continue
                    
                    # Analyze the clip
                    result = analyzer.analyze_video(video_url, streamer_name)
                    result["video_url"] = video_url
                    
                    analysis_progress[job_id]["results"].append(result)
                    analysis_progress[job_id]["completed"] += 1
                    
                except Exception as e:
                    analysis_progress[job_id]["errors"].append(f"Clip {i+1}: {str(e)}")
                    analysis_progress[job_id]["failed"] += 1
                
                # Update progress
                total_processed = analysis_progress[job_id]["completed"] + analysis_progress[job_id]["failed"]
                if total_processed >= analysis_progress[job_id]["total"]:
                    analysis_progress[job_id]["status"] = "completed"
                    analysis_progress[job_id]["completed_at"] = datetime.now().isoformat()
        
        # Start background thread
        thread = threading.Thread(target=run_batch_analysis)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "job_id": job_id,
            "total_clips": len(clips),
            "status": "started"
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Batch analysis failed: {str(e)}"}), 500

@app.route('/analyse/progress/<job_id>', methods=['GET'])
def get_analysis_progress(job_id):
    """
    GET /analyse/progress/<job_id>
    Get progress of batch analysis
    
    Response:
    {
        "job_id": "uuid",
        "status": "in_progress|completed|failed",
        "total": 10,
        "completed": 7,
        "failed": 1,
        "progress_percent": 80,
        "results": [...],
        "errors": [...]
    }
    """
    if job_id not in analysis_progress:
        return jsonify({"error": "Job not found"}), 404
    
    progress = analysis_progress[job_id]
    total_processed = progress["completed"] + progress["failed"]
    progress_percent = (total_processed / progress["total"]) * 100 if progress["total"] > 0 else 0
    
    return jsonify({
        "job_id": job_id,
        "status": progress["status"],
        "total": progress["total"],
        "completed": progress["completed"],
        "failed": progress["failed"],
        "progress_percent": round(progress_percent, 1),
        "results": progress["results"],
        "errors": progress["errors"],
        "started_at": progress.get("started_at"),
        "completed_at": progress.get("completed_at")
    }), 200

@app.route('/patchwork/streams', methods=['GET'])
def get_patchwork_streams():
    """
    GET /patchwork/streams
    Proxy endpoint to get streams from Patchwork API
    """
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'patchwork_system'))
        
        from patchwork_clips_analyzer import PatchworkClipsAnalyzer
        
        api_key = "gv4Gp1OeZhF5eBNU7vDjDL-yqZ6vrCfdCzF7HGVMiCs"
        patchwork = PatchworkClipsAnalyzer(api_key)
        
        streams = patchwork.get_all_streams()
        
        if streams:
            return jsonify({
                "count": len(streams),
                "streams": streams
            }), 200
        else:
            return jsonify({
                "count": 0,
                "streams": [],
                "message": "No streams found"
            }), 200
            
    except Exception as e:
        return jsonify({"error": f"Failed to fetch streams: {str(e)}"}), 500

@app.route('/patchwork/clips', methods=['GET'])
def get_patchwork_clips():
    """
    GET /patchwork/clips?limit=20&username=coscu
    Proxy endpoint to get clips from Patchwork API
    """
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'patchwork_system'))
        
        from patchwork_clips_analyzer import PatchworkClipsAnalyzer
        
        api_key = "gv4Gp1OeZhF5eBNU7vDjDL-yqZ6vrCfdCzF7HGVMiCs"
        patchwork = PatchworkClipsAnalyzer(api_key)
        
        limit = int(request.args.get('limit', 20))
        username = request.args.get('username', '')
        
        if username:
            # Get clips for specific streamer
            # First get streams to find the stream ID
            streams = patchwork.get_all_streams()
            stream_id = None
            
            for stream in streams:
                if stream.get('username', '').lower() == username.lower():
                    stream_id = stream.get('_id')
                    break
            
            if stream_id:
                clips = patchwork.get_clips_for_stream(stream_id, limit)
            else:
                clips = []
        else:
            # Get all clips
            clips = patchwork.get_all_clips(limit)
        
        return jsonify({
            "count": len(clips),
            "clips": clips,
            "username": username if username else "all"
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch clips: {str(e)}"}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """
    GET /stats
    Get system statistics
    """
    try:
        # Get database stats
        total_videos = len(db.search_videos())
        
        # Get Patchwork stats
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'patchwork_system'))
        
        from patchwork_clips_analyzer import PatchworkClipsAnalyzer
        
        api_key = "gv4Gp1OeZhF5eBNU7vDjDL-yqZ6vrCfdCzF7HGVMiCs"
        patchwork = PatchworkClipsAnalyzer(api_key)
        
        streams = patchwork.get_all_streams()
        clips = patchwork.get_all_clips(limit=100)  # Sample for stats
        
        # Calculate stats
        streamers = list(set([stream.get('username', 'Unknown') for stream in streams]))
        platforms = list(set([stream.get('type', 'Unknown') for stream in streams]))
        
        return jsonify({
            "total_analyzed_videos": total_videos,
            "total_available_streams": len(streams),
            "total_available_clips": len(clips),
            "unique_streamers": len(streamers),
            "platforms": platforms,
            "sample_streamers": streamers[:10],
            "last_updated": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get stats: {str(e)}"}), 500

@app.route('/find_clips', methods=['POST'])
def find_clips():
    """
    POST /find_clips
    Searches for clips based on search query and/or tags
    
    Request body:
    {
        "search_query": "Some video title",
        "tags": []
    }
    
    Response:
    {
        "title": "Some video title",
        "description": "Some video description",
        "tags": ["trending", "n3on"],
        "upload_date": "2025-04-02"
    }
    """
    try:
        # Get request data with proper JSON error handling
        try:
            data = request.get_json()
        except Exception as e:
            return jsonify({
                "error": "Invalid JSON format"
            }), 400
        
        if not data:
            return jsonify({
                "error": "Request body is required"
            }), 400
        
        search_query = data.get('search_query', '')
        tags = data.get('tags', [])
        
        # Validate that at least one search parameter is provided
        if not search_query and not tags:
            return jsonify({
                "error": "At least one of 'search_query' or 'tags' must be provided"
            }), 400
        
        # Search for videos
        results = db.search_videos(search_query=search_query, tags=tags)
        
        # Format response - return all matches
        if results:
            videos = []
            for video in results:
                videos.append({
                    "title": video.get("title", ""),
                    "description": video.get("description", ""),
                    "tags": video.get("tags", []),
                    "upload_date": video.get("upload_date", ""),
                    "video_url": video.get("video_url", "")
                })
            
            return jsonify({
                "count": len(videos),
                "videos": videos
            }), 200
        else:
            return jsonify({
                "message": "No clips found matching the search criteria",
                "count": 0,
                "videos": []
            }), 404
        
    except Exception as e:
        print(f"Error in /find_clips: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "error": f"Search failed: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Patchwork Library Analyzer + Search API"
    }), 200

@app.route('/videos', methods=['GET'])
def list_videos():
    """List all analyzed videos (for debugging/admin purposes)"""
    try:
        results = db.search_videos()
        return jsonify({
            "count": len(results),
            "videos": results
        }), 200
    except Exception as e:
        return jsonify({
            "error": f"Failed to list videos: {str(e)}"
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error"
    }), 500

if __name__ == '__main__':
    print("Starting Patchwork Library Analyzer + Search API...")
    print(f"Server running on http://{config.API_HOST}:{config.API_PORT}")
    
    app.run(
        host=config.API_HOST,
        port=config.API_PORT,
        debug=config.DEBUG
    ) 