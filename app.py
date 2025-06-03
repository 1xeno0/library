from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
from analyse import VideoAnalyzer
from config import Config

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize video analyzer
try:
    analyzer = VideoAnalyzer()
    print("✅ Application initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize application: {e}")
    analyzer = None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        if analyzer is None:
            return jsonify({
                'status': 'error',
                'message': 'Video analyzer not initialized'
            }), 500
        
        # Check database connection
        video_count = analyzer.db.get_video_count()
        
        return jsonify({
            'status': 'healthy',
            'message': 'Video Analysis API is running',
            'video_count': video_count,
            'version': '1.0.0'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Health check failed: {str(e)}'
        }), 500

@app.route('/analyse', methods=['POST'])
def analyze_video():
    """Analyze video from URL."""
    try:
        if analyzer is None:
            return jsonify({
                'success': False,
                'error': 'Video analyzer not initialized'
            }), 500
        
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        video_url = data.get('video_link')
        
        if not video_url:
            return jsonify({
                'success': False,
                'error': 'video_link is required'
            }), 400
        
        # Analyze video
        result = analyzer.analyze_video(video_url)
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        print(f"❌ Error in analyze_video: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/find_clips', methods=['POST'])
def find_clips():
    """Search for video clips."""
    try:
        if analyzer is None:
            return jsonify({
                'success': False,
                'error': 'Video analyzer not initialized'
            }), 500
        
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        search_query = data.get('search_query')
        tags = data.get('tags')
        
        if not search_query and not tags:
            return jsonify({
                'success': False,
                'error': 'Either search_query or tags must be provided'
            }), 400
        
        # Search videos
        result = analyzer.search_videos(query=search_query, tags=tags)
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Error in find_clips: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/videos', methods=['GET'])
def get_videos():
    """Get all analyzed videos."""
    try:
        if analyzer is None:
            return jsonify({
                'success': False,
                'error': 'Video analyzer not initialized'
            }), 500
        
        # Get all videos
        result = analyzer.get_all_videos()
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Error in get_videos: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({
        'success': False,
        'error': 'Method not allowed'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    try:
        # Validate configuration before starting
        Config.validate_config()
        
        print(f"🚀 Starting Video Analysis API on {Config.API_HOST}:{Config.API_PORT}")
        print(f"📊 Debug mode: {Config.DEBUG}")
        
        app.run(
            host=Config.API_HOST,
            port=Config.API_PORT,
            debug=Config.DEBUG
        )
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        print("\n💡 Make sure you have:")
        print("1. Set OPENAI_API_KEY environment variable")
        print("2. MongoDB running (or set MONGODB_URI)")
        print("3. All dependencies installed")
        print("\nRun: python fix_dependencies.py to fix dependency issues") 