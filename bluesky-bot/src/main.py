import os
import schedule
import time
from datetime import datetime
from generator.reading_generator import ReadingGenerator
from animator.video_creator import VideoCreator
from poster.bluesky_poster import BlueskyPoster
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_daily_reading():
    """Generate and post the daily tarot reading."""
    try:
        # Initialize components
        generator = ReadingGenerator()
        video_creator = VideoCreator()
        poster = BlueskyPoster()

        # Generate reading
        logger.info("Generating daily reading...")
        reading_data = generator.get_daily_reading()
        
        # Create video
        logger.info("Creating video...")
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        video_path = os.path.join(output_dir, f"reading_{reading_data['date']}.mp4")
        video_creator.create_video(reading_data, video_path)
        
        # Post to Bluesky
        logger.info("Posting to Bluesky...")
        success = poster.post_reading(reading_data, video_path)
        
        if success:
            logger.info("Daily reading posted successfully!")
        else:
            logger.error("Failed to post daily reading")
            
    except Exception as e:
        logger.error(f"Error in daily reading process: {e}")

def main():
    """Main function to schedule and run the daily reading."""
    # Schedule the reading for 9 AM every day
    schedule.every().day.at("09:00").do(create_daily_reading)
    
    logger.info("Daily tarot reading bot started. Will post at 9 AM daily.")
    
    # Run the scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main() 