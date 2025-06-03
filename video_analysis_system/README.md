# Video Analysis System

A Flask-based API system for analyzing video content using OpenAI's vision capabilities and storing results in MongoDB.

## 🆕 Recent Improvements (Fixed 404 Errors!)

**✅ Enhanced Video Download System:**
- **Fixed 404 errors** - Now properly handles invalid/non-existent video URLs
- **yt-dlp integration** - Supports 1000+ video platforms (YouTube, Twitch, Vimeo, etc.)
- **Better error messages** - Clear guidance on supported URL types
- **URL validation** - Checks URLs before attempting download
- **Proper HTTP status codes** - 400 for client errors, 500 for server errors

**🎯 Now Supports:**
- YouTube (`youtube.com`, `youtu.be`)
- Twitch (`twitch.tv`, `clips.twitch.tv`) 
- Vimeo, Dailymotion, Facebook, Instagram, TikTok
- Direct video files (`.mp4`, `.avi`, `.mov`, etc.)
- 1000+ other platforms via yt-dlp

See `FIX_SUMMARY.md` for detailed technical information about the improvements.

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

### Analyze Video ⭐ (Enhanced!)
```http
POST /analyse
Content-Type: application/json

{
    "video_link": "https://youtube.com/watch?v=example"
}
```

**Now supports:**
- ✅ YouTube, Twitch, Vimeo URLs
- ✅ Direct video file URLs (if accessible)
- ✅ 1000+ other platforms

**Error responses:**
- `400` - Invalid URL with helpful error message
- `500` - Server processing error

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

## 🧪 Testing URL Validation

Test the improved error handling:

```bash
python3 test_url_validation.py
```

This will test various URL types and show you the improved error messages.

## 🔧 Configuration

All configuration is done through environment variables. See `env_example.txt` for all available options.

### Key Settings:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `MONGODB_URI`: MongoDB connection string
- `FRAME_EXTRACTION_INTERVAL`: Seconds between frame extractions (default: 5)
- `MAX_FRAMES_FOR_ANALYSIS`: Maximum frames to send to OpenAI (default: 5)

## 🐛 Troubleshooting

### Common Issues:

1. **404 Video Not Found (FIXED!):**
   - ✅ Now returns helpful error: "Video file not found (404). Please check if the URL is correct..."
   - ✅ Suggests using supported platforms like YouTube, Twitch, etc.

2. **Unsupported URL (IMPROVED!):**
   - ✅ Clear message: "Unsupported URL. Supported: YouTube, Twitch, Vimeo, direct video files..."
   - ✅ Lists all supported platform types

3. **pyOpenSSL/cryptography error:**
   - Run `python fix_dependencies.py`
   - Or manually install compatible versions as shown above

4. **MongoDB connection error:**
   - Make sure MongoDB is running
   - Check your `MONGODB_URI` in `.env`

5. **OpenAI API error:**
   - Verify your `OPENAI_API_KEY` is correct
   - Check your OpenAI account has credits

### Dependency Versions:

The system uses these specific versions to avoid compatibility issues:
- `cryptography==41.0.8`
- `pyOpenSSL==23.3.0`
- `pymongo==4.6.0`
- `yt-dlp>=2023.11.16` (NEW!)

## 🚀 Features

- **Enhanced Video Download**: Robust downloading with yt-dlp + direct file fallback
- **URL Validation**: Pre-download validation with helpful error messages  
- **AI-Powered Content Recognition**: Uses OpenAI GPT-4o-mini for intelligent content analysis
- **MongoDB Storage**: Persistent storage with search capabilities
- **RESTful API**: Clean JSON API with proper HTTP status codes
- **Duplicate Detection**: Avoids re-analyzing the same video
- **Comprehensive Error Handling**: Clear, actionable error messages

## 📁 Project Structure

```
video_analysis_system/
├── app.py                    # Main Flask application
├── analyse.py               # Video analysis logic (ENHANCED!)
├── database.py              # MongoDB operations
├── video.py                 # Video processing utilities
├── config.py                # Configuration management
├── requirements.txt         # Python dependencies (updated)
├── fix_dependencies.py      # Dependency fixer script
├── test_url_validation.py   # URL validation tests (NEW!)
├── FIX_SUMMARY.md          # Detailed fix documentation (NEW!)
├── env_example.txt          # Environment variables example
└── README.md               # This file
```

## 🔒 Security Notes

- Never commit your `.env` file with real API keys
- Use environment variables for all sensitive configuration
- Consider using MongoDB Atlas for production deployments
- Implement rate limiting for production use

## 📝 License

This project is provided as-is for educational and development purposes. 