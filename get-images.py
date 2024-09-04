import csv
import os
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_image(url, save_path):
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        with open(save_path, 'wb') as img_file:
            for chunk in response.iter_content(chunk_size=8192):
                img_file.write(chunk)
        return f"Downloaded: {os.path.basename(save_path)}"
    except requests.exceptions.RequestException as e:
        return f"Failed to download {url}: {str(e)}"

def process_row(row, image_dir):
    image_url = row['URL']
    filename = os.path.basename(image_url)
    save_path = os.path.join(image_dir, filename)
    return download_image(image_url, save_path)

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the CSV file
csv_file = os.path.join(current_dir, 'resultados-macedonia-del-norte.csv')

# Create a directory to store downloaded images
image_dir = os.path.join(current_dir, 'downloaded_images')
os.makedirs(image_dir, exist_ok=True)

# Open and read the CSV file
with open(csv_file, 'r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    rows = list(csv_reader)

# Set up threading pool
max_workers = 5  # Limit concurrent connections
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = [executor.submit(process_row, row, image_dir) for row in rows]
    
    # Process results as they complete
    for future in as_completed(futures):
        print(future.result())
        time.sleep(0.1)  # Add a small delay between requests

print("Image download complete.")


