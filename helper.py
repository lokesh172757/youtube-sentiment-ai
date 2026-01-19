from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
import pandas as pd
import streamlit as st

# --- CONFIGURATION ---
try:
    API_KEY = st.secrets[api_key]
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
            
            comments_data.append([author, text, likes])

        # 4. Return as DataFrame
        df = pd.DataFrame(comments_data, columns=['Author', 'Comment', 'Likes'])
        return df

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
    else:
        print("Error:", result)