# Daily Tarot Reading Bluesky Bot

A bot that generates daily tarot readings and posts them to Bluesky with an animated video.

## Features

- Generates daily tarot readings using OpenAI
- Creates animated videos with card flips and text overlays
- Posts to Bluesky on a schedule
- Supports both Major and Minor Arcana cards
- Includes upright and reversed card positions

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your credentials:
```
OPENAI_API_KEY=your_openai_api_key
BLUESKY_HANDLE=your_bluesky_handle
BLUESKY_PASSWORD=your_bluesky_password
```

3. Set up the assets:
- Place card images in `assets/cards/` (named as `card_name.png`, e.g., `the_fool.png`)
- Add a card back image as `assets/cards/back.png`
- Add a background image as `assets/background.png`

## Usage

Run the bot:
```bash
python src/main.py
```

The bot will:
1. Generate a daily reading at 9 AM
2. Create an animated video
3. Post to Bluesky

## Project Structure

```
bluesky-bot/
├── assets/
│   └── cards/          # Card images
├── src/
│   ├── generator/      # Reading generation
│   ├── animator/       # Video creation
│   ├── poster/         # Bluesky posting
│   └── main.py         # Main script
├── output/             # Generated videos
├── requirements.txt    # Dependencies
└── README.md          # This file
```

## Notes

- The bot currently posts a still image from the video since Bluesky doesn't support video uploads
- Card images should be in PNG format
- The reading is generated using GPT-4 for best results 