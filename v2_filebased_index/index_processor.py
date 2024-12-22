# install libraries in console befor running script: pip install nltk, pip install PyPDF2
import os
import json
import re
import time
from datetime import datetime
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from PyPDF2 import PdfReader
import traceback

# load stopwords while first program run, if you don't want to use an individual set of stopwords:
# import nltk
# nltk.download('stopwords')

# Initialize variables
file_index = {}
search_index = {}
error_count = 0
success_count = 0
supported_filetypes = [".pdf", ".txt", ".csv", ".py", ".ipynb", ".html"]
stemmer = SnowballStemmer("german")
script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the script directory as root path for output files
log_file = os.path.join(script_dir, "index_error.log")
stopwords_file = os.path.join(script_dir, "stopwords.txt")

# Load individual set of stopwords, if not existing, load nltk-preset stopwords
if os.path.exists(stopwords_file):
    with open(stopwords_file, "r") as f:
        stop_words = set(word.strip() for word in f.readlines())
else:
    stop_words = set(stopwords.words("german"))

# Function to clean and process text
def process_text(text):
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)  # Remove special characters
    text = text.lower()  # Convert to lowercase
    words = text.split() # Split text into separated words
    words = [stemmer.stem(word) for word in words if word not in stop_words]  # Stem words and remove stopwords
    return words

# Function to extract metadata from a file
def extract_metadata(filepath):
    try:
        stat = os.stat(filepath)
        metadata = {
            "Filename": os.path.basename(filepath),
            "Path": filepath,
            "Author": "Unknown",  # Placeholder, as author extraction varies by file type
            "CreateDate": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            "Pages": 0  # Placeholder for non-PDF files
        }
        return metadata
    except Exception as e:
        log_error(filepath, str(e))
        return None

# Function to log errors
def log_error(filepath, message):
    global error_count
    error_count += 1
    with open(log_file, "a") as log:
        log.write(f"Error processing {filepath}: {message}\n")

# Main processing function
def process_files(folder_path):
    global success_count
    file_id = 0
    for root, _, files in os.walk(folder_path): # iterate trough folder structure to get every file
        for file in files:
            filepath = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()

            metadata = extract_metadata(filepath)
            current_file = metadata["Filename"]
            if not metadata:
                continue

            if file_ext not in supported_filetypes:
                log_error(filepath, "Unsupported file type") # log unsupported files into error-log
                print(f"\033[91mIndexing error: {current_file}\033[0m")
                continue
            
            file_id += 1
            file_index[file_id] = metadata

            try:
                if file_ext == ".pdf":
                    reader = PdfReader(filepath)
                    metadata["Pages"] = len(reader.pages)
                    metadata["Author"] = reader.metadata.get("/Author", "Unknown")  # Extract author if available
                    for page_number, page in enumerate(reader.pages, start=1):
                        text = page.extract_text()
                        words = process_text(text)
                        #print(words)
                        for word in words:
                            if word not in search_index:
                                search_index[word] = {}
                            if file_id not in search_index[word]:
                                search_index[word][file_id] = {}
                            if page_number not in search_index[word][file_id]:
                                search_index[word][file_id][page_number] = 0
                            search_index[word][file_id][page_number] += 1

                elif file_ext in [".txt", ".csv", ".py", ".ipynb", ".html"]:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()
                        words = process_text(text)
                        for word in words:
                            if word not in search_index:
                                search_index[word] = {}
                            if file_id not in search_index[word]:
                                search_index[word][file_id] = {}
                            if 1 not in search_index[word][file_id]:
                                search_index[word][file_id][1] = 0
                            search_index[word][file_id][1] += 1

                print(f"Indexed file successfully: {current_file}")
                success_count += 1

            except Exception as e:
                log_error(filepath, traceback.format_exc())

# Save indices to CSV
def save_to_json(data, filename, script_dir):
    filepath = os.path.join(script_dir, filename)
    with open(filepath, "w", encoding="utf-8") as jsonfile:
        json.dump(data, jsonfile, indent=4, ensure_ascii=False)

# Main script execution
if __name__ == "__main__":
    #folder_to_index = input("Enter the folder path to index: ")
    folder_to_index = r"C:\Users\s.mueller\GitHub\IR_Project_search_engine\v2_filebased_index\data_small"

    t = time.time()

    process_files(folder_to_index)

    # Save file_index
    save_to_json(file_index, r"indices\file_index.json", script_dir)

    # Save search_index
    save_to_json(search_index, r"indices\search_index.json", script_dir)

    print(f"\nIndexing complete. Successfully indexed files: {success_count}, Errors: {error_count}")
    print(f"\nProcessing time: {round(time.time()-t, 2)}"," s")
