# Patchwork API Data Fetcher

This script fetches recent data from the Patchwork API (https://patchwork.gobbo.gg) including streams and clips.

## Setup

1. Install dependencies:
```bash
pip install -r patchwork_requirements.txt
```

2. Make the script executable (optional):
```bash
chmod +x patchwork_data_fetcher.py
```

## Usage

### Basic Usage
```bash
python3 patchwork_data_fetcher.py
```

This will:
- Fetch all streams from the API
- Fetch all clips from the API  
- Fetch clips for each individual stream
- Save all data to timestamped JSON files
- Display a summary of the fetched data

### Command Line Options

```bash
python3 patchwork_data_fetcher.py [options]
```

**Available Options:**
- `--no-save` - Don't save data to files (display only)
- `--debug` - Enable debug mode with connection testing
- `--mock` - Use mock data instead of API (for testing)
- `--help` - Show help message and API key instructions

### Examples

**No-Save Mode:**
```bash
python3 patchwork_data_fetcher.py --no-save
```

**Debug Mode:**
```bash
python3 patchwork_data_fetcher.py --debug
```

**Mock Data Mode (for testing):**
```bash
python3 patchwork_data_fetcher.py --mock
```

**Combined Options:**
```bash
python3 patchwork_data_fetcher.py --mock --no-save
```

## Output Files

When run in normal mode (without `--no-save`), the script creates these files:

- `YYYYMMDD_HHMMSS_patchwork_streams.json` - All streams data
- `YYYYMMDD_HHMMSS_patchwork_clips.json` - All clips data  
- `YYYYMMDD_HHMMSS_patchwork_complete_data.json` - Complete dataset including clips by stream
- `YYYYMMDD_HHMMSS_patchwork_mock_data.json` - Mock data (when using `--mock`)

## API Endpoints Used

- `GET /streams` - Fetches all streams
- `GET /clips` - Fetches all clips
- `GET /clips/stream/{stream_id}` - Fetches clips for a specific stream

## Features

- ✅ Comprehensive data fetching from all available endpoints
- ✅ Automatic file saving with timestamps
- ✅ Error handling and retry logic
- ✅ Rate limiting (0.5s delay between stream-specific requests)
- ✅ Data analysis and summary reporting
- ✅ Support for no-save mode
- ✅ Detailed logging and progress indicators
- ✅ Mock data mode for testing
- ✅ Debug mode with connection testing
- ✅ Comprehensive troubleshooting guidance

## API Key Configuration

The API key is currently hardcoded in the script. To use your own API key:

1. Open `patchwork_data_fetcher.py`
2. Find the line: `API_KEY = "Ab3dE5Fg7Hi9Jk1Lm3NoPq-StUvWxYz0123456789AB"`
3. Replace with your actual API key

### Getting a Valid API Key

1. Visit the Patchwork website: https://patchwork.gobbo.gg
2. Sign up for an account or log in
3. Navigate to your account settings or developer section
4. Generate a new API key
5. Replace the API_KEY variable in the script

## Troubleshooting

### 401 Unauthorized Error

If you get a 401 Unauthorized error:
- Check if your API key is valid and active
- Verify you have the correct permissions
- Contact the Patchwork team for API access

### Testing Without Valid API Key

Use mock mode to test the script functionality:
```bash
python3 patchwork_data_fetcher.py --mock
```

### Debug Mode

For detailed connection testing:
```bash
python3 patchwork_data_fetcher.py --debug
```

## Example Output

### Successful API Fetch
```
🚀 Starting Patchwork API data fetch...
📡 API Base URL: https://patchwork.gobbo.gg
🔑 Using API Key: Ab3dE5Fg7H...
--------------------------------------------------
📺 Fetching streams...
✅ Successfully fetched 5 streams
💾 Data saved to 20250123_143022_patchwork_streams.json

🎬 Fetching all clips...
✅ Successfully fetched 25 clips
💾 Data saved to 20250123_143022_patchwork_clips.json

🔍 Fetching clips for each stream...
  📹 Fetching clips for stream: LofiGirl
✅ Successfully fetched clips for stream 678ef66b9083a4518f3030a6

💾 Saving complete dataset...
💾 Data saved to 20250123_143022_patchwork_complete_data.json

==================================================
📊 FETCH SUMMARY:
   Streams: 5
   All Clips: 25
   Streams with clips: 1
==================================================

🔍 ANALYZING RECENT ACTIVITY:
------------------------------
📺 Total Streams: 5
   1. LofiGirl (youtube)
   2. StreamerName2 (twitch)
   ...

🎬 Total Clips: 25
   Recent clips found: 25

📊 Clips by Stream Analysis:
   Stream 678ef66b9083a4518f3030a6: 12 clips

✅ Data fetch completed successfully!
📁 Check the generated JSON files for detailed data
```

### Mock Data Mode
```
🎭 Mock data mode enabled
📝 Running in no-save mode (data won't be saved to files)
🚀 Starting Patchwork API data fetch...
📡 API Base URL: https://patchwork.gobbo.gg
🔑 Using API Key: Ab3dE5Fg7H...
--------------------------------------------------
🎭 Using mock data mode
🎭 Generating mock data for testing...

🔍 ANALYZING RECENT ACTIVITY:
------------------------------
📝 Note: This analysis is based on mock data
📺 Total Streams: 2
   1. TestStreamer1 (youtube)
   2. TestStreamer2 (twitch)

🎬 Total Clips: 2
   Recent clips found: 2

📊 Clips by Stream Analysis:
   Stream mock_stream_1: 1 clips
   Stream mock_stream_2: 1 clips

✅ Data fetch completed successfully!
```

### API Key Issues
```
🔍 Testing API connection and authentication...
   Testing Public clips endpoint: GET /clips
   ❌ Unauthorized: 401 - {"message":"Unauthorized","statusCode":401}
   Testing Streams endpoint (requires auth): GET /streams
   ❌ Unauthorized: 401 - {"message":"Unauthorized","statusCode":401}

⚠️  API connection test failed.
🔧 This could mean:
   - Your API key is invalid or expired
   - The API endpoints have changed
   - Network connectivity issues
   - API server is down

💡 Try running with --mock to test with sample data
💡 Or check your API key with the Patchwork team
``` 