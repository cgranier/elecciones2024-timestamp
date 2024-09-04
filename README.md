# Image Timestamp Extractor

## Description

This project is designed to extract timestamps from a series of images using Optical Character Recognition (OCR). It processes a CSV file containing image URLs, downloads the images, performs OCR to extract timestamps, and updates the CSV with the results. The script includes features such as image rotation for improved timestamp detection and efficient handling of previously processed files.

## Features

- Extracts timestamps from images using OCR
- Handles large datasets efficiently
- Resumes interrupted processing
- Rotates images if timestamps are not initially detected
- Deduplicates entries in the output CSV
- Saves rotated images for further analysis

## Requirements

- Python 3.6+
- Tesseract OCR
- Python libraries: PIL (Pillow), pytesseract, requests

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/elecciones2024-timestamp.git
   cd elecciones2024-timestamp
   ```

2. Install required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Tesseract OCR:
   - For Windows: Download and install from [GitHub Tesseract-OCR](https://github.com/UB-Mannheim/tesseract/wiki)
   - For macOS: `brew install tesseract`
   - For Linux: `sudo apt-get install tesseract-ocr`

4. Set the path to Tesseract executable in the script if it's not in your system PATH.

## Usage

1. Prepare your input CSV file (e.g., `resultados-macedonia-del-norte.csv`) with at least a 'URL' column containing image URLs.

2. Update the script with your specific file paths and settings:
   - `input_csv`: Path to your input CSV file
   - `output_csv`: Path for the output CSV file
   - `image_dir`: Directory where downloaded images are stored

3. Run the script:
   ```bash
   python ocr-time.py
   ```

4. The script will process the images and update the output CSV file with extracted timestamps.

## Output

- Updated CSV file with a new 'timestamp' column
- Rotated images (if any) saved with '_rotated' suffix in the image directory

## Troubleshooting

- If Tesseract is not found, ensure it's installed and the path is correctly set in the script.
- For issues with image processing, check the image directory permissions and available disk space.

## Contributing

Contributions to improve the script or extend its functionality are welcome. Please submit a pull request or open an issue to discuss proposed changes.

## License

[MIT License](LICENSE)

## Contact

For any queries or support, please open an issue in the GitHub repository.
