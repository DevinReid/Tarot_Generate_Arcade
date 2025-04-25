import os
from datetime import datetime
from atproto import Client, models
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def post_card_flip():
    print("Starting post_card_flip function...")
    
    # Initialize Bluesky client
    print("Initializing Bluesky client...")
    client = Client()
    
    # Login to Bluesky
    print("Attempting to login to Bluesky...")
    try:
        client.login(
            os.getenv('BLUESKY_USERNAME'),
            os.getenv('BLUESKY_PASSWORD')
        )
        print("Successfully logged in to Bluesky")
    except Exception as e:
        print(f"Error during login: {str(e)}")
        raise
    
    # Get current date for the daily tarot post
    current_date = datetime.now().strftime("%B %d, %Y")
    print(f"Current date: {current_date}")
    
    # Prepare the post text
    post_text = f"✨ Daily Tarot Reading - {current_date} ✨\n\n"
    post_text += "The cards have been drawn and the future awaits...\n\n"
    post_text += "Experience the magic of tarot in our upcoming game, Mama Nyah's House of Tarot! 🎮✨\n\n"
    post_text += "🔮 #Tarot #Gaming #IndieGame #Steam #TarotReading #GamingCommunity"
    print("Post text prepared:")
    print(post_text)
    
    # Path to the video file
    video_path = os.path.join(os.path.dirname(__file__), '..', 'card_flip.mp4')
    print(f"Video path: {video_path}")
    print(f"Video file exists: {os.path.exists(video_path)}")
    
    # Upload the video
    print("Reading video file...")
    try:
        with open(video_path, 'rb') as f:
            video_data = f.read()
        print(f"Video file read successfully. Size: {len(video_data)} bytes")
    except Exception as e:
        print(f"Error reading video file: {str(e)}")
        raise
    
    # Create the post with video
    print("Attempting to upload video...")
    try:
        # First, upload the video using the standard blob upload
        print("Calling upload_blob...")
        upload_response = client.upload_blob(video_data)
        print(f"Upload response: {upload_response}")
        
        # Create the video embed
        print("Creating video embed...")
        video_embed = {
            '$type': 'app.bsky.embed.recordWithMedia',
            'record': {
                '$type': 'app.bsky.embed.record',
                'record': {
                    '$type': 'com.atproto.repo.strongRef',
                    'uri': f"at://{os.getenv('BLUESKY_USERNAME')}/app.bsky.feed.post/{datetime.now().isoformat()}",
                    'cid': upload_response.blob.ref.link
                }
            },
            'media': {
                '$type': 'app.bsky.embed.video',
                'video': upload_response.blob,
                'alt': 'Tarot card flip animation'
            }
        }
        print(f"Video embed created: {video_embed}")
        
        # Send the post with the video embed
        print("Attempting to send post...")
        client.send_post(
            text=post_text,
            embed=video_embed
        )
        print("Post sent successfully!")
    except Exception as e:
        print(f"Error during upload/post: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Error details: {dir(e)}")
        raise
    
    print("Successfully posted card flip animation to Bluesky!")

if __name__ == "__main__":
    post_card_flip() 