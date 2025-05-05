from PIL import Image
import requests
import io
import os

photoroom_key = os.getenv("PHOTOROOM_KEY")

def remove_bg(image_path):
    """
    Remove background from image using PhotoRoom API and return image bytes (JPEG).
    """
    url = "https://sdk.photoroom.com/v1/segment"

    with open(image_path, "rb") as img_file:
        files = {
            "image_file": img_file
        }
        headers = {
            "Accept": "image/png",
            "x-api-key": photoroom_key
        }

        response = requests.post(url, files=files, headers=headers)

    if response.status_code == 200:
        image_data = io.BytesIO(response.content)

        # Convert PNG bytes to Image
        png_image = Image.open(image_data).convert("RGBA")

        # Add white background
        white_bg = Image.new("RGB", png_image.size, (255, 255, 255))
        white_bg.paste(png_image, mask=png_image.split()[3])  # Use alpha channel as mask

        # Save to in-memory bytes
        output_buffer = io.BytesIO()
        white_bg.save(output_buffer, format="JPEG")
        output_buffer.seek(0)
        return output_buffer
    else:
        raise Exception(f"PhotoRoom API error: {response.status_code} - {response.text}")