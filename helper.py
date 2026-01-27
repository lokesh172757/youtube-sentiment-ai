from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
import pandas as pd
import streamlit as st

# --- CONFIGURATION ---
try:
    API_KEY = st.secrets["api_key"]
except:
    API_KEY = "LOCAL_KEY_FOR_TESTING"

def get_video_id(url):
    """
    Extracts the 'v' parameter from a YouTube URL.
    Example: https://www.youtube.com/watch?v=dQw4w9WgXcQ -> dQw4w9WgXcQ
    """
    try:
        # This handles standard urls, short urls (youtu.be), and mobile urls
        if "youtu.be" in url:
            return url.split("/")[-1]
        
        query = urlparse(url).query
        params = parse_qs(query)
        return params["v"][0]
    except:
        return None

def fetch_comments(video_url):
    """
    Connects to YouTube API and fetches the top 100 comments.
    """
    video_id = get_video_id(video_url)
    
    if not video_id:
        return {"error": "Invalid YouTube URL"}

    try:
        # 1. Connect to YouTube
        youtube = build("youtube", "v3", developerKey=API_KEY)

        # 2. Request Comments
        # 'snippet' contains the text, author, and likes
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,  # Grab 100 comments
            order="relevance" # Get the 'top' comments (most likely to be interesting)
        )
        response = request.execute()

        # 3. Process the JSON response into a list
        comments_data = []
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            text = comment['textDisplay']
            author = comment['authorDisplayName']
            likes = comment['likeCount']
            replies = item['snippet']['totalReplyCount']
            published = comment['publishedAt']
            
            comments_data.append([author, text, likes, replies, published])

        # 4. Return as DataFrame
        df = pd.DataFrame(comments_data, columns=['Author', 'Comment', 'Likes', 'Reply_Count', 'Published_At'])
        return df

    except Exception as e:
        return {"error": str(e)}

def get_channel_id(video_url):
    """
    Finds the Channel ID from a video URL.
    """
    video_id = get_video_id(video_url)
    if not video_id: return None
    
    try:
        youtube = build("youtube", "v3", developerKey=API_KEY)
        request = youtube.videos().list(part="snippet", id=video_id)
        response = request.execute()
        return response['items'][0]['snippet']['channelId']
    except:
        return None

def fetch_channel_videos(channel_id, limit=5):
    """
    Fetches the last N videos from a channel.
    Returns: List of tuples (video_url, title, published_at)
    """
    try:
        youtube = build("youtube", "v3", developerKey=API_KEY)
        
        # 1. Get Uploads Playlist ID
        ch_req = youtube.channels().list(part="contentDetails", id=channel_id)
        ch_res = ch_req.execute()
        uploads_id = ch_res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # 2. Get Videos from Playlist
        pl_req = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_id,
            maxResults=limit
        )
        pl_res = pl_req.execute()
        
        videos = []
        for item in pl_res['items']:
            vid_id = item['snippet']['resourceId']['videoId']
            title = item['snippet']['title']
            pub = item['snippet']['publishedAt']
            url = f"https://www.youtube.com/watch?v={vid_id}"
            videos.append({'url': url, 'title': title, 'published': pub})
            
        return videos
    except Exception as e:
        return {"error": str(e)}

# --- MENTOR CHECK ---
# Run this file directly to test if your API Key works!
if __name__ == "__main__":
    test_url = "https://www.youtube.com/watch?v=oM4dI1wn21I&t=633s" #  video URL
    print("Testing API connection...")
    result = fetch_comments(test_url)
    
    if isinstance(result, pd.DataFrame):
        print(f"Success! Fetched {len(result)} comments.")
        print(result.head())
        
        # Test Channel Logic
        print("\nTesting Channel Fetch...")
        cid = get_channel_id(test_url)
        print(f"Channel ID: {cid}")
        if cid:
            vids = fetch_channel_videos(cid)
            print(f"Found {len(vids)} recent videos.")
    else:
        print("Error:", result)