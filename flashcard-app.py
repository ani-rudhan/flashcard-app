
from flask import Flask, render_template
import csv
from pathlib import Path
import os

app = Flask(__name__)

def combine_vocab_files():
    """
    Checks for the existence of 'n5-vocab - TopicX.csv' (X=1 to 24)
    and combines them into a single CSV file, dropping all headers,
    using only Python's built-in 'csv' module.
    """
    
    # 1. Configuration
    base_filename = "n5-vocab - Topic"
    file_range_start = 1
    file_range_end = 24  # Loop will go up to and including 24
    output_filename = "n5-vocab.csv"
    header_row = ['Topic', 'Audio', 'Word', 'Kanji', 'Meaning', 'Notes']
    found_files_count = 0
    total_rows_written = 0

    print(f"Starting CSV consolidation. Looking for files from {base_filename}1.csv up to {base_filename}{file_range_end}.csv")

    # 2. Open the output file once in write mode
    # newline='' is essential for cross-platform CSV writing in Python 3
    all_data_written = False
    try:
        with open(output_filename, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(header_row)

            # 3. Iterate and Collect Data
            for i in range(file_range_start, file_range_end + 1):
                filename = f"{base_filename}{i}.csv"
                file_path = Path(filename)
                
                if file_path.is_file():
                    found_files_count += 1
                    all_data_written = True
                    print(f"✅ Found and reading: {filename}")
                    
                    try:
                        # Open the input file
                        with open(file_path, 'r', newline='', encoding='utf-8') as infile:
                            reader = csv.reader(infile)
                            
                            # Crucial step: Skip the header row of the current input file
                            try:
                                next(reader) 
                            except StopIteration:
                                # Handles the case of an empty input file
                                print(f"   -> File is empty (Skipping).")
                                continue
                                
                            # Write all remaining rows (the data) to the output file
                            rows_written_in_file = 0
                            for row in reader:
                                writer.writerow(row)
                                rows_written_in_file += 1
                                
                            total_rows_written += rows_written_in_file
                            print(f"   -> Appended {rows_written_in_file} data rows.")
                            
                    except Exception as e:
                        print(f"⚠️ Error reading or writing data from {filename}: {e}")
                else:
                    print(f"❌ File not found: {filename}")

    except Exception as e:
        print(f"🔴 An error occurred while handling the output file: {e}")
        return
    
    if not all_data_written:
        print("No CSV files were found to combine. Exiting.")
        # Attempt to clean up the potentially created empty output file
        try:
            os.remove(output_filename)
        except OSError:
            pass
        return

    print(f"Successfully combined data from {found_files_count} files.")
    print(f"Total rows written to file: {total_rows_written}")
    print("-" * 30)
    print(f"✅ Success! All data saved to {output_filename}")

# The filename used in the user's original snippet
VOCAB_FILENAME = "n5-vocab.csv" 

@app.route('/')
def index():
    """
    Reads the CSV file using the built-in csv library, identifies and drops 
    the 'Unnamed: 0' column if present, and prepares the data for the template.
    """
    cards = []
    
    try:
        # Open the file and prepare the CSV reader
        with open(VOCAB_FILENAME, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            
            # --- 1. Get the header (column names) ---
            try:
                header = next(reader)
            except StopIteration:
                # Handle empty file case (no header or data)
                return render_template('index_app.html', cards=[]) 

            # --- 2. Check for and prepare to drop 'Unnamed: 0' ---
            column_to_drop_name = 'Unnamed: 0'
            should_drop = False
            drop_index = -1
            
            try:
                # Find the index of the column to drop
                drop_index = header.index(column_to_drop_name)
                
                # Remove the column name from the header list (to be used as keys)
                header.pop(drop_index) 
                should_drop = True
            except ValueError:
                # 'Unnamed: 0' column not found, no need to drop
                pass

            # --- 3. Process the data rows ---
            for row in reader:
                # Filter the row data if the column needs to be dropped
                if should_drop:
                    # Create a new list for the row data, skipping the element at drop_index
                    data_row = [data for i, data in enumerate(row) if i != drop_index]
                else:
                    data_row = row

                # Ensure the number of data elements matches the number of header keys
                if len(data_row) == len(header):
                    # 4. Create the dictionary for the card
                    # dict(zip) maps the header names (keys) to the data elements (values)
                    card_dict = dict(zip(header, data_row))
                    cards.append(card_dict)
                else:
                    # Log or skip rows that are malformed (e.g., too few columns)
                    print(f"Skipping malformed row due to length mismatch: {row}")

    except FileNotFoundError:
        print(f"Error: Required file {VOCAB_FILENAME} not found.")
        # Pass an error message to the template for user feedback
        return render_template('index_app.html', cards=[], error="Data file missing.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return render_template('index_app.html', cards=[], error=f"An unexpected error occurred.")

    print(f"Rendering template")
    # 5. Render the template
    return render_template('index_app.html', cards=cards)

if __name__ == '__main__':
    combine_vocab_files()
    app.run(debug=True)
