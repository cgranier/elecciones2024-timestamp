import csv

# Input and output file names
input_file = 'resultados-with-timestamps.csv'
output_file = 'urls_with_nf.csv'

# Open the input CSV file for reading
with open(input_file, mode='r', newline='') as infile:
    reader = csv.DictReader(infile)
    
    # Prepare to write to the output CSV file
    with open(output_file, mode='w', newline='') as outfile:
        writer = csv.writer(outfile)
        
        # Write header for the output CSV
        writer.writerow(['URL'])
        
        # Iterate through each row in the input CSV
        for row in reader:
            # Check if 'NF' is in the 'timestamp' column
            if 'NF' in row['timestamp']:
                # Write the 'URL' column value to the output CSV
                writer.writerow([row['URL']])

print(f"URLs have been written to {output_file}")
