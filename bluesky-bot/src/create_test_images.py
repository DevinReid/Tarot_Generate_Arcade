from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_image(size, text, color, output_path):
    """Create a placeholder image with text."""
    img = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(img)
    
    # Try to load a font, fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Center the text
    text_width = draw.textlength(text, font=font)
    text_height = 40
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    
    # Draw text
    draw.text(position, text, fill="white", font=font)
    img.save(output_path)

def main():
    # Create assets directory if it doesn't exist
    os.makedirs("assets/cards", exist_ok=True)
    
    # Create placeholder images
    card_size = (300, 500)
    
    # Create card front
    create_placeholder_image(
        card_size,
        "The Fool",
        "blue",
        "assets/cards/the_fool.png"
    )
    
    # Create card back
    create_placeholder_image(
        card_size,
        "Tarot",
        "purple",
        "assets/cards/back.png"
    )
    
    # Create background
    create_placeholder_image(
        (1920, 1080),
        "Daily Tarot Reading",
        "black",
        "assets/background.png"
    )
    
    print("Placeholder images created successfully!")

if __name__ == "__main__":
    main() 