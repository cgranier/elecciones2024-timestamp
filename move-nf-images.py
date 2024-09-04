import os
import shutil
import csv
from urllib.parse import urlparse

# Input and output directory paths
downloaded_images_dir = 'downloaded_images'
nf_images_dir = 'nf_images'
urls_file = 'urls_with_nf.csv'

# Create the output directory if it doesn't exist
os.makedirs(nf_images_dir, exist_ok=True)

# Read the URLs from the CSV file
with open(urls_file, mode='r', newline='') as infile:
    reader = csv.reader(infile)
    next(reader)  # Skip header
    
    for row in reader:
        url = row[0]
        
        # Extract the filename from the URL
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        # Define source and destination paths
        src = os.path.join(downloaded_images_dir, filename)
        dst = os.path.join(nf_images_dir, filename)
        
        # Check if the file exists and copy it to the destination folder
        if os.path.exists(src):
            shutil.copy(src, dst)
            print(f"Copied: {filename}")
        else:
            print(f"File not found: {filename}")

print("File copying process completed.")
