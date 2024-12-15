import mysql.connector
from datetime import datetime
from typing import Optional, Tuple, List


class DatabaseConnector:
    def __init__(self, host="127.0.0.1", port=3306, user="root", password="rootroot", database="cas_course_data"):
        """Initialize the MySQL database connection"""
        self.db = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.db.cursor()
        self._init_database()

    def _init_database(self):
        """Initialize database with proper tables"""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS content (
            id INT AUTO_INCREMENT PRIMARY KEY,
            file_path VARCHAR(500),
            content LONGTEXT,
            file_type VARCHAR(50),
            module VARCHAR(200),
            topic VARCHAR(200),
            subtopic VARCHAR(200),
            chapter VARCHAR(200),
            instructor VARCHAR(100),
            page_number INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            word_count INT
        );
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_references (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_path VARCHAR(500) UNIQUE,
                file_type VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INT AUTO_INCREMENT PRIMARY KEY,
                content_id INT,
                tag VARCHAR(100),
                weight FLOAT,
                FOREIGN KEY (content_id) REFERENCES content(id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS processing_errors (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_path VARCHAR(500),
                error_message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.db.commit()

    def store_content(self, file_path: str, content: str, metadata: dict, file_type: str) -> int:
        """Store processed content in the database"""
        word_count = len(content.split()) if content else 0
        insert_query = """
            INSERT INTO content 
            (file_path, content, file_type, module, topic, subtopic, chapter, instructor, page_number, created_at, word_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)
        """
        # Ensure file_path is converted to string
        self.cursor.execute(insert_query, (
            str(file_path), content, file_type,
            metadata.get('module'), metadata.get('topic'),
            metadata.get('subtopic'), metadata.get('chapter'),
            metadata.get('instructor'), metadata.get('page_number'),
            word_count
        ))
        self.db.commit()
        return self.cursor.lastrowid


    def store_file_reference(self, file_path: str, file_type: str, metadata: Optional[str] = None):
        """Store a reference to unprocessed or binary files"""
        insert_query = """
            INSERT INTO file_references 
            (file_path, file_type, created_at, metadata)
            VALUES (%s, %s, NOW(), %s)
        """
        self.cursor.execute(insert_query, (file_path, file_type, metadata))
        self.db.commit()

    def store_error(self, file_path: str, error_message: str):
        """Store processing errors in the database"""
        insert_query = """
            INSERT INTO processing_errors 
            (file_path, error_message, timestamp)
            VALUES (%s, %s, NOW())
        """
        self.cursor.execute(insert_query, (str(file_path), error_message))
        self.db.commit()

    def fetch_all_content(self) -> List[Tuple]:
        """Fetch all content from the database"""
        self.cursor.execute("SELECT * FROM content")
        return self.cursor.fetchall()

    def update_content(self, module: Optional[str], topic: Optional[str], 
                       instructor: Optional[str], file_path: str):
        """Update content metadata in the database with length validation"""
        if module:
            module = module[:200]
        if topic:
            topic = topic[:200]
        if instructor:
            instructor = instructor[:100]  # Adjusted for new schema
            
        update_query = """
        UPDATE content 
        SET module = %s, topic = %s, instructor = %s 
        WHERE file_path = %s
        """
        self.cursor.execute(update_query, (module, topic, instructor, file_path))
        self.db.commit()

    def close(self):
        """Close the database connection"""
        self.cursor.close()
        self.db.close()
