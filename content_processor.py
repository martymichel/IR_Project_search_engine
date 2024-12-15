import os
import logging
import time
import traceback
from pathlib import Path
from processors import TextProcessor, PDFProcessor
from db_connector import DatabaseConnector

class ContentProcessor:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.db = DatabaseConnector(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="rootroot",
            database="cas_course_data"
        )
        self.processed_files = 0
        self.total_files = 0
        self.total_words = 0
        self.errors = 0

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('processing.log', mode='w'),
                logging.StreamHandler()
            ]
        )

        self.processors = {
            '.py': TextProcessor(self.db),
            '.sql': TextProcessor(self.db),
            '.pdf': PDFProcessor(self.db)
        }


    def process_directory(self):
        """Process all files in the directory recursively"""
        try:
            # Count total files first
            logging.info(f"Scanning directory: {self.root_dir}")
            for file_path in self.root_dir.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in self.processors:
                    self.total_files += 1
            
            if self.total_files == 0:
                logging.warning("No supported files found in directory")
                return
            
            logging.info(f"Found {self.total_files} files to process")
            
            # Process files
            for file_path in self.root_dir.rglob('*'):
                if file_path.is_file():
                    self.process_file(file_path)
                    
        except Exception as e:
            error_msg = f"Error processing directory: {str(e)}\n{traceback.format_exc()}"
            logging.error(error_msg)
            print(f"\nError processing directory: {str(e)}")

    def process_file(self, file_path):
        """Process a single file based on its extension"""
        try:
            ext = file_path.suffix.lower()
            
            if ext in self.processors:
                # Update progress
                self.processed_files += 1
                progress = (self.processed_files / self.total_files) * 100
                
                # Process file
                processor = self.processors[ext]
                try:
                    logging.info(f"Processing {file_path}")
                    content_id, word_count = processor.process(file_path)
                    
                    if content_id is not None:
                        self.total_words += word_count
                        logging.info(f"Successfully processed: {file_path} ({word_count} words)")
                    
                    # Show progress with proper spacing
                    print(f"\rProgress: {progress:.1f}% | Files: {self.processed_files}/{self.total_files} | Words: {self.total_words}      ", end="\n" if progress == 100 else "")
                    
                except Exception as e:
                    self.errors += 1
                    error_msg = f"Error processing {file_path}: {str(e)}\n{traceback.format_exc()}"
                    logging.error(error_msg)
                    print(f"\nError processing {file_path}: {str(e)}")

        except Exception as e:
            self.errors += 1
            error_msg = f"Error handling {file_path}: {str(e)}\n{traceback.format_exc()}"
            logging.error(error_msg)
            print(f"\nError handling {file_path}: {str(e)}")

def main():
    # Record start time
    start_time = time.time()

    # Start message
    print("CAS Content Processor")
    print("====================")
    
    # Get directory path from user input
    directory = input("\nEnter the directory path to process: ")
    
    if not os.path.isdir(directory):
        print("Error: Invalid directory path")
        return
    
    # Initialize and run processor
    processor = ContentProcessor(directory)
    processor.process_directory()

    # Record end time
    end_time = time.time()
    processing_time = end_time - start_time
    
    # Print summary with proper spacing
    print("\n\nProcessing Summary")
    print("=================")
    print(f"Total files found: {processor.total_files}")
    print(f"Files processed: {processor.processed_files}")
    print(f"Words extracted: {processor.total_words}")
    print(f"Errors encountered: {processor.errors}")
    print(f"Processing time: {processing_time:.2f} seconds")
    
    # Show log file location with absolute path
    log_path = os.path.abspath('processing.log')
    print(f"\nFor detailed processing log, check: {log_path}")

if __name__ == "__main__":
    main()