import os
import re
import csv
from urllib.parse import urlparse
from PIL import Image
import pytesseract

# Set the path to the Tesseract executable if it's not in your PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_timestamp(image_path, box):
    with Image.open(image_path) as img:
        cropped = img.crop(box)
        text = pytesseract.image_to_string(cropped)
        time_pattern = r'\b([01]\d|2[0-3]):([0-5]\d)(:([0-5]\d))?\b'
        matches = re.findall(time_pattern, text)
        return ':'.join(filter(None, matches[0])) if matches else "NF"

def extract_filename(url):
    return os.path.basename(urlparse(url).path)

def process_image(image_path, initial_box, larger_box):
    # Try with initial box
    timestamp = extract_timestamp(image_path, initial_box)
    if timestamp != "NF":
        return timestamp, False

    # Try with larger box
    timestamp = extract_timestamp(image_path, larger_box)
    if timestamp != "NF":
        return timestamp, False

    # If still not found, try rotating the image
    file_name, file_extension = os.path.splitext(image_path)
    rotated_img_path = f"{file_name}_rotated{file_extension}"
    
    with Image.open(image_path) as img:
        rotated_img = img.rotate(180)
        rotated_img.save(rotated_img_path)

    # Try OCR on rotated image
    timestamp = extract_timestamp(rotated_img_path, initial_box)
    if timestamp == "NF":
        timestamp = extract_timestamp(rotated_img_path, larger_box)

    return timestamp, True

# Define the initial crop box
initial_crop_box = (300, 400, 650, 600)

# Input and output CSV files
input_csv = "resultados-macedonia-del-norte.csv"
output_csv = "resultados-with-timestamps.csv"

# Image directory
image_dir = "downloaded_images"

# Read all existing data from the output CSV if it exists
existing_data = {}
if os.path.exists(output_csv):
    with open(output_csv, 'r', newline='', encoding='utf-8') as existing_file:
        reader = csv.DictReader(existing_file)
        for row in reader:
            url = row['URL']
            if url not in existing_data or row['timestamp'] != "NF":
                existing_data[url] = row

# Process images and update existing data
for url, row in existing_data.items():
    filename = extract_filename(url)
    image_path = os.path.join(image_dir, filename)
    
    if row['timestamp'] != "NF":
        print(f"Skipping already processed file: {filename}")
        continue
    
    if os.path.exists(image_path):
        with Image.open(image_path) as img:
            width, height = img.size
            larger_crop_box = (0, 0, width, height // 4)
        
        timestamp, was_rotated = process_image(image_path, initial_crop_box, larger_crop_box)
        if was_rotated:
            print(f"Image was rotated: {filename}")
    else:
        timestamp = "NF"
    
    row['timestamp'] = timestamp
    print(f"Processed: {filename}, Timestamp: {timestamp}")

# Write the updated data back to the output CSV
with open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
    fieldnames = list(next(iter(existing_data.values())).keys()) if existing_data else ['URL', 'timestamp']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(existing_data.values())

print("Processing complete. Results written to", output_csv)
