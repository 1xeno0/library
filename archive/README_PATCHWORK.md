# Patchwork API Data Fetcher

A Python script to fetch recent streams and clips data from the Patchwork API (https://patchwork.gobbo.gg).

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r patchwork_requirements.txt
   ```

2. **Test with mock data:**
   ```bash
   python3 patchwork_data_fetcher.py --mock --no-save
   ```

3. **Use with your API key:**
   - Edit `patchwork_data_fetcher.py`
   - Replace the `API_KEY` variable with your actual key
   - Run: `python3 patchwork_data_fetcher.py`

## 📁 Files

- **`patchwork_data_fetcher.py`** - Main script for fetching data
- **`test_patchwork_api.py`** - API testing utility
- **`patchwork_requirements.txt`** - Python dependencies
- **`PATCHWORK_USAGE.md`** - Detailed usage guide

## 🔧 Features

- ✅ Fetch streams and clips from Patchwork API
- ✅ Save data to timestamped JSON files
- ✅ Mock data mode for testing
- ✅ Debug mode with connection testing
- ✅ Comprehensive error handling
- ✅ Rate limiting for API requests
- ✅ Data analysis and reporting

## 📊 API Endpoints

The script uses these Patchwork API endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/streams` | GET | Fetch all streams |
| `/clips` | GET | Fetch all clips |
| `/clips/stream/{id}` | GET | Fetch clips for specific stream |

## 🔑 Authentication

The script uses API key authentication via the `x-api-key` header. You'll need a valid API key from Patchwork.

### Getting an API Key

1. Visit https://patchwork.gobbo.gg
2. Sign up or log in
3. Navigate to account settings/developer section
4. Generate a new API key
5. Update the script with your key

## 🎯 Usage Examples

### Basic Usage
```bash
# Fetch all data and save to files
python3 patchwork_data_fetcher.py

# Fetch data without saving
python3 patchwork_data_fetcher.py --no-save

# Test with mock data
python3 patchwork_data_fetcher.py --mock

# Debug mode with connection testing
python3 patchwork_data_fetcher.py --debug
```

### Testing API Connection
```bash
# Test different authentication methods
python3 test_patchwork_api.py
```

## 📄 Output

The script generates timestamped JSON files:

- `YYYYMMDD_HHMMSS_patchwork_streams.json` - All streams
- `YYYYMMDD_HHMMSS_patchwork_clips.json` - All clips
- `YYYYMMDD_HHMMSS_patchwork_complete_data.json` - Complete dataset

## 🔍 Sample Output

```json
{
  "fetch_timestamp": "2025-01-23T14:30:22.123456",
  "streams": [
    {
      "id": "stream_123",
      "username": "StreamerName",
      "type": "youtube",
      "created_at": "2025-01-20T10:00:00Z"
    }
  ],
  "clips": [
    {
      "id": "clip_456",
      "title": "Amazing Moment",
      "stream_id": "stream_123",
      "created_at": "2025-01-20T10:15:00Z",
      "duration": 30
    }
  ],
  "clips_by_stream": {
    "stream_123": [...]
  }
}
```

## 🛠️ Troubleshooting

### 401 Unauthorized
- Check if your API key is valid
- Verify API key permissions
- Contact Patchwork support

### Connection Issues
- Check internet connectivity
- Verify API endpoints are accessible
- Try debug mode: `--debug`

### Testing Without API Key
Use mock mode to test functionality:
```bash
python3 patchwork_data_fetcher.py --mock
```

## 📋 Requirements

- Python 3.6+
- `requests` library
- Valid Patchwork API key (for live data)

## 🤝 Support

For API access or issues:
- Visit https://patchwork.gobbo.gg
- Contact the Patchwork team
- Check their documentation

## 📝 License

This script is provided as-is for educational and development purposes. 