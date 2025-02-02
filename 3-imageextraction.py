import os
import re
import base64
import json

# Define folder paths
folder_x = r"C:\Users\Koen\Documents\GitHub\kalorme.github.io"  # Folder containing HTML files
folder_y = r"C:\Users\Koen\Documents\GitHub\kalorme.github.io\images\recipe"  # Folder to store images

# Ensure folder Y exists
os.makedirs(folder_y, exist_ok=True)

# Function to extract Base64 image from an HTML file
def extract_base64_image(html_file):
    with open(html_file, "r", encoding="utf-8") as file:
        content = file.read()

    # Improved regex to properly capture Base64 images with escaped slashes
    match = re.search(r'"image"\s*:\s*"data:image\\/jpeg;base64,([^"]+)"', content)

    if match:
        base64_data = match.group(1).replace("\\/", "/")  # Replace escaped slashes if needed
        print(f"[DEBUG] Extracted Base64 data (first 50 chars): {base64_data[:50]}...")
        return base64_data
    else:
        print(f"[ERROR] No image found in: {html_file}")
        return None

# Scan Folder X for HTML files
for filename in os.listdir(folder_x):
    if filename.endswith(".html") and filename != "index.html":
        html_path = os.path.join(folder_x, filename)
        image_filename = filename.replace(".html", ".jpg")
        image_path = os.path.join(folder_y, image_filename)

        # Check if the image already exists in Folder Y
        if os.path.exists(image_path):
            print(f"Image already exists: {image_path}")
            continue

        # Extract Base64 image from the HTML file
        base64_data = extract_base64_image(html_path)
        if base64_data:
            try:
                # Decode and save the image
                with open(image_path, "wb") as img_file:
                    img_file.write(base64.b64decode(base64_data))
                print(f"✅ Extracted and saved: {image_path}")
            except Exception as e:
                print(f"[ERROR] Failed to save image {image_path}: {e}")
        else:
            print(f"❌ No image extracted from: {html_path}")