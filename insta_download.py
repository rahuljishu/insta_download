import streamlit as st
import instaloader
import os
import re
from pathlib import Path
import shutil

def extract_shortcode_from_url(url):
    """Extract the Instagram shortcode from a URL."""
    pattern = r'instagram.com/(?:p|reel|tv)/([^/?]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def download_instagram_video(url, quality='high'):
    """
    Download Instagram video using instaloader.
    
    Parameters:
    - url: Instagram post URL
    - quality: Video quality ('high' or 'low')
    
    Returns:
    - tuple: (success status, file path or error message)
    """
    try:
        # Initialize instaloader
        L = instaloader.Instaloader(
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )
        
        # Extract shortcode from URL
        shortcode = extract_shortcode_from_url(url)
        if not shortcode:
            return False, "Invalid Instagram URL"
        
        # Create temporary directory
        temp_dir = Path("temp_downloads")
        temp_dir.mkdir(exist_ok=True)
        
        # Download post
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        # Download video
        if quality == 'high':
            L.download_post(post, target=temp_dir)
        else:
            # For low quality, modify instaloader settings
            L.download_video_thumbnails = True
            L.download_videos = False
            L.download_post(post, target=temp_dir)
        
        # Find downloaded video file
        video_file = None
        for file in temp_dir.glob("*.mp4"):
            video_file = file
            break
        
        if not video_file:
            return False, "No video found in the post"
        
        return True, video_file
    
    except instaloader.exceptions.InstaloaderException as e:
        return False, f"Instagram error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    st.title("Instagram Video Downloader")
    st.write("Download Instagram videos in your preferred quality")
    
    # User input
    url = st.text_input("Enter Instagram Video URL:")
    quality = st.radio(
        "Select Video Quality",
        ('High Quality', 'Low Quality'),
        index=0
    )
    
    if st.button("Download Video"):
        if not url:
            st.error("Please enter a valid Instagram URL")
            return
        
        with st.spinner("Downloading video..."):
            success, result = download_instagram_video(
                url,
                'high' if quality == 'High Quality' else 'low'
            )
            
            if success:
                # Read video file
                video_data = result.read_bytes()
                
                # Create download button
                st.download_button(
                    label="Click to Download",
                    data=video_data,
                    file_name=result.name,
                    mime="video/mp4"
                )
                
                # Clean up
                try:
                    shutil.rmtree("temp_downloads")
                except:
                    pass
            else:
                st.error(result)

    st.markdown("---")
    st.markdown("""
    ### Instructions:
    1. Paste the Instagram video/reel URL in the text box
    2. Select your preferred video quality
    3. Click the "Download Video" button
    4. Once processing is complete, click "Click to Download" to save the video
    
    ### Note:
    - This app requires a stable internet connection
    - Some videos might not be available for download due to privacy settings
    - Please respect copyright and Instagram's terms of service
    """)

if __name__ == "__main__":
    main()
