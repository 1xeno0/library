import requests

# Configuration
API_KEY = "gv4Gp1OeZhF5eBNU7vDjDL-yqZ6vrCfdCzF7HGVMiCs"
BASE_URL = "https://patchwork.gobbo.gg"
USERNAME = "jynxzi"
PAGE = 0
LIMIT = 1  # Only the first clip

# Headers
headers = {
    "x-api-key": API_KEY
}

def save_error_to_html(content, filename="error_response.html"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Error response saved to {filename}")

try:
    # Get clips
    response = requests.get(
        f"{BASE_URL}/clips",
        headers=headers,
        params={
            "username": USERNAME,
            "page": PAGE,
            "limit": LIMIT
        }
    )

    if response.status_code != 200:
        save_error_to_html(response.text)
        raise Exception(f"Failed to fetch clips: {response.status_code}")

    clips = response.json()
    if not clips:
        raise Exception("No clips found.")

    first_clip = clips[0]
    print("Clip metadata:", first_clip)

    # Try to get video URL
    clip_url = first_clip.get("videoUrl") or first_clip.get("url")
    if not clip_url:
        raise Exception("Clip URL not found in the response.")

    video_resp = requests.get(clip_url)
    if video_resp.status_code != 200:
        save_error_to_html(video_resp.text)
        raise Exception("Failed to download the clip video file.")

    with open("first_clip.mp4", "wb") as f:
        f.write(video_resp.content)
    print("Clip downloaded as first_clip.mp4")

except Exception as e:
    print("Error:", e)
