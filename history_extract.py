import csv

# Input and output file names
input_file = 'raw_data/download-files-firefox-linux-3.csv'
output_file = 'raw_data_filtered/filtered_output_5.csv'

# Read and filter the CSV
with open(input_file, mode='r', newline='', encoding='utf-8') as infile, \
        open(output_file, mode='w', newline='', encoding='utf-8') as outfile:

    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)

    # Write the header
    writer.writeheader()

    # Filter rows
    for row in reader:
        if "History" in row['source_long']:
            writer.writerow(row)

print(f"Filtered rows saved to {output_file}")
2
