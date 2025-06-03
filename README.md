# Patchwork Library Analyzer System

A comprehensive system for fetching video clips from Patchwork API and analyzing them using AI-powered video analysis **with streaming focus**.

## 🎮 New Streaming Features

### ✨ **Enhanced for Streamers & Gaming Content**
- **🎤 Audio Transcription**: Automatically extracts and includes audio transcripts using OpenAI Whisper
- **📺 Streamer Detection**: Identifies streamers from visual cues, overlays, and usernames
- **🎮 Gaming Context**: Specialized analysis for gaming content, reactions, and streaming moments
- **💬 Chat Integration**: Analyzes visible chat messages and viewer interactions
- **🏷️ Streaming Tags**: Generates tags specific to streaming content (game titles, emotions, platform, etc.)

### 🔍 **Streaming-Specific Analysis**
- **Platform Detection**: Identifies Twitch, YouTube, or other streaming platforms
- **Game Recognition**: Detects and identifies games being played
- **Content Classification**: Gaming, Just Chatting, Creative, IRL content types
- **Moment Highlights**: Epic plays, fails, funny moments, clutch plays, rage moments
- **Stream Elements**: Overlays, alerts, donations, raids, hosts

## 📁 Directory Structure

```
Library For Patchwork/
├── README.md                           # This file - main documentation
├── test_streaming_analysis.py          # Test script for new streaming features
├── video_analysis_system/              # Core video analysis API
│   ├── app.py                         # Flask API server (enhanced for streaming)
│   ├── analyse.py                     # Video analysis with transcript & streaming focus
│   ├── database.py                    # MongoDB integration
│   ├── video.py                       # Video processing utilities
│   ├── config.py                      # Configuration settings
│   ├── requirements.txt               # Python dependencies (includes moviepy)
│   ├── test_video_analysis.py         # Video analysis tests
│   ├── test_video_search.py           # Video search tests
│   ├── run_all_tests.py               # Test runner
│   └── test_api.py                    # API endpoint tests
├── patchwork_system/                   # Patchwork clips analyzer
│   ├── patchwork_clips_analyzer.py    # Main tool (enhanced with streamer info)
│   └── requirements.txt               # Patchwork dependencies
├── results/                            # Analysis results storage
│   └── *.json                         # Timestamped analysis results
└── archive/                            # Old/deprecated files
    ├── transcript.py                  # Original transcript code (now integrated)
    └── ...                            # Previous versions and misc files
```

## 🚀 Quick Start

### 1. Set Up Video Analysis API

```bash
cd video_analysis_system
pip install -r requirements.txt

# Configure your environment variables
export OPENAI_API_KEY="your_openai_api_key"
export MONGODB_URI="your_mongodb_connection_string"
export PORT=5051

# Start the video analysis API
python app.py
```

### 2. Test the Enhanced Streaming Analysis

```bash
# Run comprehensive tests
python3 test_streaming_analysis.py
```

### 3. Run Patchwork Clips Analysis with Streaming Focus

```bash
cd patchwork_system

# Analyze clips with enhanced streaming analysis
python3 patchwork_clips_analyzer.py --all-clips --streamers=5 --clips=10

# Test with mock data
python3 patchwork_clips_analyzer.py --mock --streamers=3 --clips=5
```

## 📋 Enhanced API Features

### Video Analysis API (`video_analysis_system/`)

**Enhanced for streaming content analysis:**

- **`app.py`** - Flask REST API with streaming-focused endpoints:
  - `POST /analyse` - **Enhanced**: Now accepts `streamer_name` parameter
  - `GET /find_clips` - Search with streaming-specific tags
  - `GET /videos` - List all analyzed videos
  - `GET /health` - Health check

- **`analyse.py`** - **Enhanced** video analysis engine:
  - **🎤 Audio transcription** using OpenAI Whisper
  - **📺 Streamer detection** from visual cues
  - **🎮 Gaming-focused** AI prompts
  - **💬 Chat analysis** and viewer engagement
  - **🏷️ Streaming tags** generation

### Enhanced API Request/Response

```bash
# Enhanced analyse endpoint
curl -X POST http://localhost:5051/analyse \
  -H "Content-Type: application/json" \
  -d '{
    "video_link": "https://pw-clips.gobbo.gg/clips/coscu/clip.mp4",
    "streamer_name": "coscu"
  }'

# Enhanced response with streaming data
{
  "title": "Epic Gaming Clutch - Coscu's Amazing Play",
  "description": "Detailed description including streaming context and transcript...",
  "tags": ["coscu", "gaming", "clutch", "epic", "twitch", "spanish"],
  "upload_date": "2025-01-31",
  "streamer": "coscu",
  "game": "Counter-Strike 2",
  "platform": "twitch",
  "content_type": "gaming",
  "transcript_included": true,
  "frames_analyzed": 5,
  "transcript_length": 245
}
```

## 🎮 Streaming-Focused Features

### 🎤 **Audio Transcription**
- Automatically extracts audio from video clips
- Uses OpenAI Whisper for high-quality transcription
- Integrates transcript into video description
- Supports multiple languages

### 📺 **Streamer Detection**
- Uses provided streamer name from Patchwork API
- Falls back to visual detection from overlays, usernames, chat
- Identifies channel branding and stream elements

### 🎮 **Gaming Content Analysis**
- **Game Recognition**: Identifies specific games being played
- **Gameplay Analysis**: Describes player actions, achievements, fails
- **UI Elements**: Analyzes game menus, HUD, character stats
- **Gaming Moments**: Epic plays, clutch moments, funny fails

### 💬 **Streaming Context**
- **Platform Detection**: Twitch, YouTube, other platforms
- **Chat Analysis**: Visible chat messages and reactions
- **Stream Overlays**: Alerts, widgets, donation notifications
- **Viewer Engagement**: Subscriber counts, viewer reactions

### 🏷️ **Enhanced Tagging System**
```json
{
  "tags": [
    "coscu",           // Streamer name
    "counter-strike",  // Game title
    "twitch",          // Platform
    "gaming",          // Content type
    "clutch",          // Moment type
    "epic",            // Emotion
    "spanish",         // Language
    "fps",             // Game genre
    "competitive"      // Game mode
  ]
}
```

## 🔍 **Search Examples for Streaming Content**

```bash
# Search for specific streamers
curl -X POST http://localhost:5051/find_clips \
  -H "Content-Type: application/json" \
  -d '{"search_query": "coscu gaming moments"}'

# Search for game-specific content
curl -X POST http://localhost:5051/find_clips \
  -H "Content-Type: application/json" \
  -d '{"tags": ["counter-strike", "clutch", "epic"]}'

# Search for platform-specific content
curl -X POST http://localhost:5051/find_clips \
  -H "Content-Type: application/json" \
  -d '{"search_query": "twitch funny moments"}'

# Search for content types
curl -X POST http://localhost:5051/find_clips \
  -H "Content-Type: application/json" \
  -d '{"tags": ["gaming", "fail", "rage"]}'
```

## 📊 Enhanced Results Format

Analysis results now include comprehensive streaming metadata:

```json
{
  "processed_clips": [
    {
      "original_clip": {
        "_id": "clip_id",
        "title": "Epic Moment",
        "username": "coscu",
        "path": "video_url"
      },
      "analysis": {
        "title": "Coscu's Epic Counter-Strike Clutch",
        "description": "Coscu performs an incredible 1v4 clutch in Counter-Strike...\n\nAudio Content: 'No way, this is impossible! I can't believe I just did that!'",
        "tags": ["coscu", "counter-strike", "clutch", "epic", "gaming", "twitch"],
        "streamer": "coscu",
        "game": "Counter-Strike 2",
        "platform": "twitch",
        "content_type": "gaming",
        "transcript_included": true,
        "transcript_length": 156,
        "frames_analyzed": 5
      },
      "processed_at": "2025-01-31T19:07:32"
    }
  ],
  "summary": {
    "total_streamers": 2,
    "total_clips": 36,
    "successful_analyses": 36,
    "success_rate": 100.0,
    "transcripts_extracted": 34,
    "games_detected": ["Counter-Strike 2", "League of Legends", "Just Chatting"],
    "platforms_detected": ["twitch", "youtube"],
    "content_types": ["gaming", "chatting", "creative"]
  }
}
```

## 🧪 Testing the Enhanced System

### Run Comprehensive Tests
```bash
# Test all streaming features
python3 test_streaming_analysis.py

# Expected output:
# ✅ Video Analysis API - Tests transcript extraction and streaming analysis
# ✅ Patchwork Pipeline - Tests API integration with streamer info
# ✅ Flask API Endpoint - Tests enhanced API with streaming parameters
```

### Manual Testing
```bash
# 1. Start the API
cd video_analysis_system && python app.py

# 2. Test with real Patchwork clips
cd patchwork_system
python3 patchwork_clips_analyzer.py --all-clips --streamers=2 --clips=3

# 3. Search for specific content
curl -X POST http://localhost:5051/find_clips \
  -H "Content-Type: application/json" \
  -d '{"search_query": "coscu epic gaming"}'
```

## 🔧 Configuration

### Environment Variables

```bash
# Required for enhanced video analysis
export OPENAI_API_KEY="your_openai_api_key_here"
export MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net/database"

# Optional
export PORT=5051                        # API port (default: 5000)
export FRAME_INTERVAL=5                 # Frame extraction interval in seconds
```

## 🚨 Troubleshooting

### Common Issues

1. **Transcript Extraction Fails**
   - Ensure moviepy is installed: `pip install moviepy`
   - Check OpenAI API key has Whisper access
   - Some videos may not have clear audio

2. **Streamer Detection Issues**
   - Provide streamer name in API request for best results
   - Visual detection works best with clear overlays/usernames

3. **Gaming Content Not Detected**
   - AI analysis depends on clear game UI elements
   - Some games may not be recognized if UI is minimal

### Debug Mode

```bash
# Enable detailed logging for streaming analysis
python3 patchwork_clips_analyzer.py --all-clips --streamers=1 --clips=1
```

## 📝 **What's New in This Version**

### ✅ **Integrated Features**
- ✅ Audio transcription using OpenAI Whisper
- ✅ Streamer name detection and integration
- ✅ Gaming-focused AI analysis prompts
- ✅ Streaming platform detection
- ✅ Enhanced tagging for streaming content
- ✅ Chat and overlay analysis
- ✅ Comprehensive test suite

### 🎯 **Streaming Focus**
- **Gaming Content**: Specialized for gaming streams, reactions, and gameplay
- **Streamer Context**: Understands streaming culture and terminology
- **Platform Awareness**: Recognizes Twitch, YouTube, and other platforms
- **Community Elements**: Analyzes chat, donations, raids, and viewer interactions

---

**Ready to analyze streaming content with AI! 🎮🤖📺**

# Video Analysis System

A Flask-based API system for analyzing video content using OpenAI's vision capabilities and storing results in MongoDB.

## 🚨 Dependency Fix for Linux

If you encounter the error:
```
TypeError: deprecated() got an unexpected keyword argument 'name'
```

This is a known compatibility issue between `pyOpenSSL` and `cryptography` libraries. Follow these steps to fix it:

### Quick Fix

1. **Run the dependency fixer:**
   ```bash
   python fix_dependencies.py
   ```

2. **Manual fix (if needed):**
   ```bash
   pip uninstall -y pyOpenSSL cryptography pymongo
   pip install cryptography==41.0.8
   pip install pyOpenSSL==23.3.0
   pip install pymongo==4.6.0
   pip install -r requirements.txt
   ```

## 🛠️ Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- MongoDB (local or MongoDB Atlas)
- OpenAI API key

### 2. Installation

1. **Clone/download the project files**

2. **Fix dependencies (Linux users):**
   ```bash
   python fix_dependencies.py
   ```

3. **Install dependencies (if fix_dependencies.py didn't work):**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   # Copy the example file
   cp env_example.txt .env
   
   # Edit .env with your actual values
   nano .env
   ```

   Required variables:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   MONGODB_URI=mongodb://localhost:27017/  # or your MongoDB Atlas URI
   ```

### 3. Running the Application

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## 📡 API Endpoints

### Health Check
```http
GET /health
```

### Analyze Video
```http
POST /analyse
Content-Type: application/json

{
    "video_link": "https://youtube.com/watch?v=example"
}
```

### Search Videos
```http
POST /find_clips
Content-Type: application/json

{
    "search_query": "cooking tutorial",
    "tags": ["cooking", "tutorial"]
}
```

### Get All Videos
```http
GET /videos
```

## 🔧 Configuration

All configuration is done through environment variables. See `env_example.txt` for all available options.

### Key Settings:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `MONGODB_URI`: MongoDB connection string
- `FRAME_EXTRACTION_INTERVAL`: Seconds between frame extractions (default: 5)
- `MAX_FRAMES_FOR_ANALYSIS`: Maximum frames to send to OpenAI (default: 5)

## 🐛 Troubleshooting

### Common Issues:

1. **pyOpenSSL/cryptography error:**
   - Run `python fix_dependencies.py`
   - Or manually install compatible versions as shown above

2. **MongoDB connection error:**
   - Make sure MongoDB is running
   - Check your `MONGODB_URI` in `.env`

3. **OpenAI API error:**
   - Verify your `OPENAI_API_KEY` is correct
   - Check your OpenAI account has credits

4. **Video download fails:**
   - Some videos may be restricted
   - Try with a different video URL
   - Check if yt-dlp supports the platform

### Dependency Versions:

The system uses these specific versions to avoid compatibility issues:
- `cryptography==41.0.8`
- `pyOpenSSL==23.3.0`
- `pymongo==4.6.0`

## 🚀 Features

- **Video Analysis**: Downloads videos and extracts frames for AI analysis
- **AI-Powered Content Recognition**: Uses OpenAI GPT-4o-mini for intelligent content analysis
- **MongoDB Storage**: Persistent storage with search capabilities
- **RESTful API**: Clean JSON API for integration
- **Duplicate Detection**: Avoids re-analyzing the same video
- **Error Handling**: Comprehensive error handling and logging

## 📁 Project Structure

```
video_analysis_system/
├── app.py                 # Main Flask application
├── analyse.py            # Video analysis logic
├── database.py           # MongoDB operations
├── video.py              # Video processing utilities
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── fix_dependencies.py   # Dependency fixer script
├── env_example.txt       # Environment variables example
└── README.md            # This file
```

## 🔒 Security Notes

- Never commit your `.env` file with real API keys
- Use environment variables for all sensitive configuration
- Consider using MongoDB Atlas for production deployments
- Implement rate limiting for production use

## 📝 License

This project is provided as-is for educational and development purposes. 